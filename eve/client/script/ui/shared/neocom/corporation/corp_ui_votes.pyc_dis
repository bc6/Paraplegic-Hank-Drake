#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/corporation/corp_ui_votes.py
import sys
import blue
import uthread
import util
import dbutil
import uix
import uiutil
import form
import listentry
import log
import uicls
import uiconst
import localization
import localizationUtil

class WizardDialogBase(uicls.Window):
    __guid__ = 'form.WizardDialogBase'

    def OnOK(self, *args):
        self.closedByOK = 1
        self.CloseByUser()

    def OnCancel(self, *args):
        self.CloseByUser()

    def GetNextStep(self):
        return self.step + 1

    def GetPreviousStep(self):
        return self.step - 1

    def OnNext(self, *args):
        self.GoToStep(self.GetNextStep())

    def OnBack(self, *args):
        self.GoToStep(self.GetPreviousStep())

    def GoToStep(self, requestedStep = 1, reload = 0):
        try:
            log.LogInfo('GoToStep requestedStep:', requestedStep, 'reload:', reload, 'self.step:', self.step)
            if self.step == requestedStep and not reload:
                log.LogInfo('GoToStep - Ignoring')
                return
            if not reload and self.steps.has_key(self.step):
                data = self.steps[self.step]
                if data is not None:
                    title, funcIn, funcOut = data
                    if funcOut is not None:
                        log.LogInfo('GoToStep - running funcOut')
                        bCan = 0
                        try:
                            bCan = funcOut(requestedStep)
                        finally:
                            self.HideLoad()

                        if not bCan:
                            log.LogInfo('GoToStep - funcOut disallowed continuation to next step')
                            return
            data = self.steps[requestedStep]
            scrolllist = []
            if data is not None:
                title, funcIn, funcOut = data
                self.SetNavigationButtons()
                log.LogInfo('GoToStep - running funcIn')
                funcIn(requestedStep, scrolllist)
                self.HideLoad()
                self.step = requestedStep
            self.HideLoad()
            self.SetHint('')
            self.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist)
            if scrolllist:
                uicore.registry.SetFocus(self.sr.scroll)
        except:
            log.LogException()
            sys.exc_clear()

    def SetNavigationButtons(self, back = 0, ok = 0, cancel = 0, next = 0):
        if self.navigationBtns is not None:
            self.navigationBtns.Close()
            self.navigationBtns = None
        else:
            uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=6)
        buttonParams = []
        buttonParams.append([localization.GetByLabel('UI/Generic/OK'),
         self.OnOK,
         (),
         66,
         0,
         1,
         0])
        buttonParams.append([localization.GetByLabel('UI/Commands/Back'),
         self.OnBack,
         (),
         66])
        buttonParams.append([localization.GetByLabel('UI/Commands/Cancel'),
         self.OnCancel,
         (),
         66])
        buttonParams.append([localization.GetByLabel('UI/Commands/Next'),
         self.OnNext,
         (),
         66,
         0,
         1,
         0])
        buttons = uicls.ButtonGroup(btns=buttonParams, parent=self.sr.main, idx=0)
        self.navigationBtns = buttons
        self.EnableNavigationButton(localization.GetByLabel('UI/Commands/Back'), back)
        self.EnableNavigationButton(localization.GetByLabel('UI/Generic/OK'), ok)
        self.EnableNavigationButton(localization.GetByLabel('UI/Commands/Cancel'), cancel)
        self.EnableNavigationButton(localization.GetByLabel('UI/Commands/Next'), next)

    def EnableNavigationButton(self, button, enabled):
        self.navigationBtns.GetBtnByLabel(button).state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][not not enabled]

    def SetSteps(self, steps, firstStep = None):
        log.LogInfo('SetSteps firstStep', firstStep)
        if firstStep is not None and not steps.has_key(firstStep):
            raise RuntimeError('SetSteps default step argument is invalid')
        self.steps = steps
        if firstStep is not None:
            self.GoToStep(firstStep)

    def SetHeading(self, heading):
        if self.heading is None:
            self.heading = uicls.EveCaptionMedium(text=heading, parent=self.sr.topParent, align=uiconst.CENTERLEFT, left=70, idx=0)
        else:
            self.heading.text = heading

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)


class VoteWizardDialog(WizardDialogBase):
    __guid__ = 'form.VoteWizardDialog'
    default_windowID = 'VoteWizardDialog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'station_inflight'
        self.heading = None
        self.step = 0
        self.navigationBtns = None
        self.voteTypes = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeCreateShares'), const.voteShares]]
        self.voteTypes.append([localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'), const.voteKickMember])
        self.voteTypes.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeGeneral'), const.voteGeneral])
        if session.stationid is not None:
            self.voteTypes.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeLockBlueprint'), const.voteItemLockdown])
            self.voteTypes.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeUnlockBlueprint'), const.voteItemUnlock])
        self.voteTypesDict = {}
        for description, value in self.voteTypes:
            self.voteTypesDict[value] = description

        self.voteType = self.voteTypes[0][1]
        self.locationID = session.stationid
        self.InitVote()
        steps = {1: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectVoteType'), self.OnSelectVoteType, None),
         3: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeCreateShares'), self.OnSelectShareVote, self.OnLeaveShareVote),
         4: (localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'), self.OnSelectExpelVote, self.OnLeaveExpelVote),
         5: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeLockBlueprint'), self.OnSelectLockdownVote, self.OnLeaveLockdownVote),
         6: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeUnlockBlueprint'), self.OnSelectUnlockVote, self.OnLeaveUnlockVote),
         7: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeGeneral'), self.OnSelectGeneralVote, self.OnLeaveGeneralVote),
         8: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteOptions'), self.OnSelectVoteOptions, self.OnLeaveVoteOptions),
         9: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteDetails'), self.OnSelectVoteDetails, self.OnLeaveVoteDetails),
         10: (localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteSummary'), self.OnSelectVoteSummary, None)}
        uix.Flush(self.sr.main)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        step = None
        if len(steps):
            step = 1
        self.SetSteps(steps, step)
        self.SetHeading(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'))
        self.SetCaption(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'))
        self.SetMinSize([400, 300])
        self.SetWndIcon('ui_7_64_9', mainTop=-2)
        self.SetTopparentHeight(58)
        return self

    def InitVote(self):
        self.ownerName = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintSelectCorporationOrAlliance')
        self.ownerID = 0
        self.voteTitle = None
        self.voteDescription = None
        self.voteDays = 1
        self.voteShares = 1
        self.memberID = 0
        self.memberName = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintSelectMember')
        self.voteOptions = []
        self.voteOptionsCount = 2
        self.itemID = 0
        self.typeID = 0
        self.flagInput = None

    def OnSelectVoteType(self, step, scrolllist):
        self.SetNavigationButtons(back=0, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('Combo', {'options': self.voteTypes,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectVoteType'),
         'cfgName': 'voteType',
         'setValue': self.voteType,
         'OnChange': self.OnComboChange,
         'name': 'voteType'}))

    def LogCurrentVoteType(self):
        log.LogInfo(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CurrentVoteType'), self.voteType, 'name:', self.voteTypesDict[self.voteType])

    def GetNextStep(self):
        log.LogInfo('GetNextStep>>')
        self.LogCurrentVoteType()
        log.LogInfo('current step:', self.step, 'detail:', self.steps[self.step])
        nextStep = None
        if self.step == 1:
            if self.voteType == const.voteShares:
                nextStep = 3
            elif self.voteType == const.voteKickMember:
                nextStep = 4
            elif self.voteType == const.voteItemLockdown:
                nextStep = 5
            elif self.voteType == const.voteItemUnlock:
                nextStep = 6
            elif self.voteType == const.voteGeneral:
                nextStep = 7
        if nextStep is None and self.step in (2, 3, 4, 5, 6, 8):
            nextStep = 9
        if nextStep is None:
            nextStep = self.step + 1
        log.LogInfo('next step:', nextStep, 'detail:', self.steps[nextStep])
        log.LogInfo('GetNextStep<<')
        return nextStep

    def GetPreviousStep(self):
        log.LogInfo('GetPreviousStep>>')
        self.LogCurrentVoteType()
        log.LogInfo('current step:', self.step, 'detail:', self.steps[self.step])
        prevStep = None
        if self.step in (2, 3, 4, 5, 6, 7):
            prevStep = 1
        if prevStep is None and self.step == 9:
            if self.voteType == const.voteShares:
                prevStep = 3
            elif self.voteType == const.voteKickMember:
                prevStep = 4
            elif self.voteType == const.voteItemLockdown:
                prevStep = 5
            elif self.voteType == const.voteItemUnlock:
                prevStep = 6
            elif self.voteType == const.voteGeneral:
                prevStep = 8
        if prevStep is None:
            prevStep = self.step - 1
        log.LogInfo('prev step:', prevStep, 'detail:', self.steps[prevStep])
        log.LogInfo('GetPreviousStep>>')
        return prevStep

    def OnSelectUnlockVote(self, step, scrolllist):
        try:
            log.LogInfo('>OnSelectUnlockVote')
            self.SetNavigationButtons(back=1, ok=0, cancel=1, next=self.itemID != 0)
            lockedItems = []
            if session.stationid is not None:
                lockedItems = sm.GetService('corp').GetLockedItemsByLocation(self.locationID)
            if len(lockedItems) == 0:
                scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintNoLockedItemsInLocation')}))
                log.LogInfo('No Corp Hangar available')
                return
            hangarItems = self.GetHangarItemsToUse()
            options = []
            if hangarItems is not None:
                options = self.GetAvailableHangars()
            options.append((localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionAllLockedItemsAtStation'), const.flagHangarAll))
            default = None
            if hangarItems is None:
                log.LogInfo('No Corp Hangar available')
                self.flagInput = const.flagHangarAll
                default = const.flagHangarAll
            if len(options):
                log.LogInfo('No options')
                if self.flagInput is not None:
                    for description, flag in options:
                        log.LogInfo('checking if ', description, flag, 'is the same as', self.flagInput)
                        if self.flagInput == flag:
                            default = flag
                            log.LogInfo('Setting default to', flag)
                            break

            if default is None:
                log.LogInfo('Default is none')
                self.flagInput = options[0][1]
                default = self.flagInput
            data = {'options': options,
             'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectItemToUnlock'),
             'cfgName': 'install_item_from',
             'setValue': default,
             'OnChange': self.OnComboChange,
             'name': 'install_item_from'}
            scrolllist.append(listentry.Get('Combo', data))
            scrolllist.append(listentry.Get('Divider'))
            if self.flagInput != const.flagHangarAll:
                self.PopulateLockedItems(scrolllist)
            else:
                self.PopulateAllLockedItems(scrolllist)
        finally:
            log.LogInfo('<OnSelectUnlockVote')

    def GenerateBlueprintExtraInfo(self, blueprint):
        infoList = []
        if blueprint.copy == 1:
            if blueprint.licensedProductionRunsRemaining != -1:
                infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CopyRuns', runsRemaining=blueprint.licensedProductionRunsRemaining))
            else:
                infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CopyRunsInfinite'))
        if blueprint.productivityLevel:
            infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProductivityLevel', productivityLevel=blueprint.productivityLevel))
        if blueprint.materialLevel:
            infoList.append(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/MaterialLevel', materialLevel=blueprint.materialLevel))
        return localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExtraInfoWrapper', extraInfo=localizationUtil.FormatGenericList(infoList))

    def PopulateAllLockedItems(self, scrolllist):
        try:
            log.LogInfo('>PopulateAllLockedItems')
            if session.stationid is None:
                return
            lockedItems = sm.GetService('corp').GetLockedItemsByLocation(self.locationID)
            listentries = []
            hangarID = self.GetHangarLocationIDToUse()
            if hangarID is None:
                hangarID = session.stationid
            blueprints = sm.RemoteSvc('factory').GetBlueprintInformationAtLocation(hangarID, 1)
            sanctionedActionsInEffect = sm.GetService('corp').GetSanctionedActionsByCorporation(session.corpid, 1)
            voteCases = sm.GetService('corp').GetVoteCasesByCorporation(session.corpid, 2)
            sanctionedActionsByLockedItemID = dbutil.CIndexedRowset(sanctionedActionsInEffect.header, 'parameter')
            if sanctionedActionsInEffect and len(sanctionedActionsInEffect):
                for sanctionedActionInEffect in sanctionedActionsInEffect.itervalues():
                    if sanctionedActionInEffect.voteType in [const.voteItemLockdown] and sanctionedActionInEffect.parameter and sanctionedActionInEffect.inEffect:
                        sanctionedActionsByLockedItemID[sanctionedActionInEffect.parameter] = sanctionedActionInEffect

            voteCaseIDByItemToUnlockID = {}
            if voteCases and len(voteCases):
                for voteCase in voteCases.itervalues():
                    if voteCase.voteType in [const.voteItemUnlock] and voteCase.endDateTime > blue.os.GetWallclockTime() - DAY:
                        options = sm.GetService('corp').GetVoteCaseOptions(voteCase.voteCaseID, voteCase.corporationID)
                        if len(options):
                            for option in options.itervalues():
                                if option.parameter:
                                    voteCaseIDByItemToUnlockID[option.parameter] = voteCase.voteCaseID

            for it in lockedItems.itervalues():
                header = ['itemID',
                 'typeID',
                 'ownerID',
                 'groupID',
                 'categoryID',
                 'quantity',
                 'locationID',
                 'flagID']
                typeInfo = cfg.invtypes.Get(it.typeID)
                line = [it.itemID,
                 it.typeID,
                 it.ownerID,
                 typeInfo.groupID,
                 typeInfo.categoryID,
                 -1,
                 self.locationID,
                 const.flagHangar]
                item = util.Row(header, line)
                if item.ownerID != session.corpid:
                    continue
                if not sanctionedActionsByLockedItemID.has_key(item.itemID):
                    continue
                if voteCaseIDByItemToUnlockID.has_key(item.itemID):
                    continue
                if item.categoryID == const.categoryBlueprint:
                    blueprint = None
                    for blueprintRow in blueprints:
                        if blueprintRow.itemID == item.itemID:
                            blueprint = blueprintRow
                            break

                    if blueprint is None:
                        log.LogInfo('Someone nabbed', item.itemID, 'while I was looking for it.')
                        continue
                    if blueprint.copy == 1 and blueprint.licensedProductionRunsRemaining == 0:
                        continue
                    description = typeInfo.name
                    extraInfo = self.GenerateBlueprintExtraInfo(blueprint)
                    data = {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockedBlueprintLabel', item=item.typeID, extraInfo=extraInfo),
                     'getIcon': 1,
                     'OnClick': self.ClickHangarItem}
                else:
                    data = {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockedItemLabel', item=item.typeID),
                     'getIcon': 1,
                     'OnClick': self.ClickHangarItem}
                listentries.append((data['label'], listentry.Get('Item', data)))

            listentries = uiutil.SortListOfTuples(listentries)
            scrolllist += listentries
        finally:
            log.LogInfo('<PopulateAllLockedItems')

    def PopulateLockedItems(self, scrolllist):
        try:
            log.LogInfo('>PopulateLockedItems')
            hangarItems = self.GetHangarItemsToUse(self.flagInput)
            if hangarItems is None:
                self.flagInput = const.flagHangarAll
                return self.PopulateAllLockedItems(scrolllist)
            listentries = []
            sm.GetService('corp').GetLockedItemsByLocation(self.locationID)
            locationID = self.GetHangarLocationIDToUse()
            blueprints = sm.RemoteSvc('factory').GetBlueprintInformationAtLocationWithFlag(locationID, self.flagInput, 1)
            sanctionedActionsInEffect = sm.GetService('corp').GetSanctionedActionsByCorporation(session.corpid, 1)
            voteCases = sm.GetService('corp').GetVoteCasesByCorporation(session.corpid, 2)
            sanctionedActionsByLockedItemID = dbutil.CIndexedRowset(sanctionedActionsInEffect.header, 'parameter')
            if sanctionedActionsInEffect and len(sanctionedActionsInEffect):
                for sanctionedActionInEffect in sanctionedActionsInEffect.itervalues():
                    if sanctionedActionInEffect.voteType in [const.voteItemLockdown] and sanctionedActionInEffect.parameter and sanctionedActionInEffect.inEffect:
                        sanctionedActionsByLockedItemID[sanctionedActionInEffect.parameter] = sanctionedActionInEffect

            voteCaseIDByItemToUnlockID = {}
            if voteCases and len(voteCases):
                for voteCase in voteCases.itervalues():
                    if voteCase.voteType in [const.voteItemUnlock] and voteCase.endDateTime > blue.os.GetWallclockTime() - DAY:
                        options = sm.GetService('corp').GetVoteCaseOptions(voteCase.voteCaseID, voteCase.corporationID)
                        if len(options):
                            for option in options.itervalues():
                                if option.parameter:
                                    voteCaseIDByItemToUnlockID[option.parameter] = voteCase.voteCaseID

            itemCount = len(hangarItems)
            for item in hangarItems:
                locked = sm.GetService('corp').IsItemLocked(item)
                extraInfo = None
                if not locked:
                    continue
                if not sanctionedActionsByLockedItemID.has_key(item.itemID):
                    continue
                if voteCaseIDByItemToUnlockID.has_key(item.itemID):
                    continue
                if item.categoryID == const.categoryBlueprint:
                    blueprint = None
                    for blueprintRow in blueprints:
                        if blueprintRow.itemID == item.itemID:
                            blueprint = blueprintRow
                            break

                    if blueprint is None:
                        log.LogInfo('Someone nabbed', item.itemID, 'while I was looking for it.')
                        continue
                    if blueprint.copy == 1 and blueprint.licensedProductionRunsRemaining == 0:
                        continue
                    itemTypeInfo = cfg.invtypes.Get(item.typeID)
                    description = itemTypeInfo.name
                    extraInfo = self.GenerateBlueprintExtraInfo(blueprint)
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockedBlueprintLabel', item=item.typeID, extraInfo=extraInfo)
                data = {'info': item,
                 'itemID': item.itemID,
                 'typeID': item.typeID,
                 'label': label,
                 'getIcon': 1,
                 'OnClick': self.ClickHangarItem}
                listentries.append((data['label'], listentry.Get('Item', data)))

            listentries = uiutil.SortListOfTuples(listentries)
            scrolllist += listentries
        finally:
            log.LogInfo('<PopulateLockedItems')

    def OnLeaveUnlockVote(self, nextStep):
        log.LogInfo('OnLeaveUnlockVote')
        if self.itemID == 0:
            if nextStep == 1:
                return 1
            return 0
        return 1

    def OnSelectLockdownVote(self, step, scrolllist):
        try:
            log.LogInfo('>OnSelectLockdownVote self.step:', self.step, ' step:', step)
            self.SetNavigationButtons(back=1, ok=0, cancel=1, next=self.itemID != 0)
            options = self.GetAvailableHangars()
            if len(options) == 0 or 0 == len(sm.GetService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('stationID', [self.locationID])):
                label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NoCorpHangarAvailable')
                scrolllist.append(listentry.Get('Header', {'label': label}))
                log.LogInfo('No Corp Hangar available')
                return
            default = None
            if self.flagInput is not None:
                for description, flag in options:
                    if self.flagInput == flag:
                        default = flag
                        break

            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectItemsToLockDown')
            data = {'options': options,
             'label': label,
             'cfgName': 'install_item_from',
             'setValue': default,
             'OnChange': self.OnComboChange,
             'name': 'install_item_from'}
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OnlyUsedBPCanBeLocked')}))
            scrolllist.append(listentry.Get('Combo', data))
            scrolllist.append(listentry.Get('Divider'))
            if default is None:
                self.flagInput = options[0][1]
            self.PopulateHangarView(scrolllist)
        finally:
            log.LogInfo('<OnSelectLockdownVote')

    def GetAvailableHangars(self, canView = 1, canTake = 0):
        try:
            log.LogInfo('>GetAvailableHangars')
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
                if canView:
                    if session.corprole & param[1] != param[1]:
                        continue
                if canTake:
                    if session.corprole & param[2] != param[2]:
                        continue
                hangarDescription = divisions[i]
                options.append((hangarDescription, param[0]))

            return options
        finally:
            log.LogInfo('<GetAvailableHangars')

    def GetHangarItemsToUse(self, flagID = None):
        try:
            log.LogInfo('>GetHangarItemsToUse')
            listing = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(session.corpid, self.locationID, 'offices')
            if len(listing):
                header = listing.header
                header.virtual = header.virtual + [('groupID', lambda i: cfg.invtypes.Get(i.typeID).groupID), ('categoryID', lambda i: cfg.invtypes.Get(i.typeID).categoryID)]
                if flagID is not None:
                    listing = [ i for i in listing if i.flagID == flagID ]
                return listing
        finally:
            log.LogInfo('<GetHangarItemsToUse')

    def GetHangarLocationIDToUse(self):
        try:
            log.LogInfo('>GetHangarLocationIDToUse')
            offices = sm.GetService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('stationID', [self.locationID])
            if len(offices):
                return offices[0].officeID
        finally:
            log.LogInfo('<GetHangarLocationIDToUse')

    def PopulateHangarView(self, scrolllist):
        try:
            log.LogInfo('>PopulateHangarView')
            sm.GetService('corp').GetLockedItemsByLocation(self.locationID)
            hangarItems = self.GetHangarItemsToUse(self.flagInput)
            listentries = []
            locationID = self.GetHangarLocationIDToUse()
            blueprints = sm.RemoteSvc('factory').GetBlueprintInformationAtLocationWithFlag(locationID, self.flagInput, 1)
            itemCount = len(blueprints)
            i = 0
            for blueprint in blueprints:
                if sm.GetService('corp').IsItemLocked(blueprint):
                    continue
                i += 1
                if not blueprint.singleton:
                    continue
                if blueprint.copy == 1:
                    continue
                itemTypeInfo = cfg.invtypes.Get(blueprint.typeID)
                description = itemTypeInfo.name
                extraInfo = self.GenerateBlueprintExtraInfo(blueprint)
                item = None
                for hangarItem in hangarItems:
                    if hangarItem.itemID == blueprint.itemID:
                        item = hangarItem
                        break

                if item is None:
                    log.LogInfo('Someone nabbed', blueprint.itemID, 'while I was looking for it.')
                    continue
                locked = sm.GetService('corp').IsItemLocked(item)
                if locked:
                    label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockedBlueprintLabel', item=item.typeID, extraInfo=extraInfo)
                else:
                    label = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/BlueprintWithSize', item=item.typeID, stacksize=item.stacksize, extraInfo=extraInfo)
                data = {'info': item,
                 'itemID': item.itemID,
                 'typeID': item.typeID,
                 'label': label,
                 'getIcon': 1,
                 'OnClick': self.ClickHangarItem}
                listentries.append((data['label'], listentry.Get('Item', data)))

            listentries = uiutil.SortListOfTuples(listentries)
            scrolllist += listentries
        finally:
            log.LogInfo('<PopulateHangarView')

    def ClickHangarItem(self, entry, *args):
        try:
            log.LogInfo('>ClickHangarItem')
            if self.voteType == const.voteItemLockdown:
                if not sm.GetService('corp').IsItemLocked(entry.sr.node.info):
                    self.SetSelectedItem(entry.sr.node.itemID, entry.sr.node.typeID)
            elif self.voteType == const.voteItemUnlock:
                if sm.GetService('corp').IsItemLocked(entry.sr.node.info):
                    self.SetSelectedItem(entry.sr.node.itemID, entry.sr.node.typeID)
        finally:
            log.LogInfo('<ClickHangarItem')

    def SetSelectedItem(self, itemID, typeID):
        try:
            log.LogInfo('>SetSelectedItem')
            self.itemID = itemID
            self.typeID = typeID
            self.SetNavigationButtons(back=1, ok=0, cancel=1, next=self.itemID != 0)
        finally:
            log.LogInfo('<SetSelectedItem')

    def OnLeaveLockdownVote(self, nextStep):
        log.LogInfo('OnLeaveLockdownVote')
        if self.itemID == 0:
            if nextStep == 1:
                return 1
            return 0
        return 1

    def PickCorporationOrAlliance(self, *args):
        dlg = form.CorporationOrAlliancePickerDailog.Open(warableEntitysOnly=True)
        dlg.ShowModal()
        if dlg.ownerID:
            if dlg.ownerID in [session.corpid, session.allianceid]:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CannotStartWarWithSelf')})
                return
            self.ownerID = dlg.ownerID
            self.ownerName = cfg.eveowners.Get(self.ownerID).ownerName
            self.GoToStep(self.step, reload=1)

    def OnSelectShareVote(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfShares'),
         'setValue': self.voteShares,
         'name': 'voteSharesCtrl',
         'intmode': (1, 10000000)}))

    def OnLeaveShareVote(self, nextStep):
        control = uiutil.GetChild(self, 'voteSharesCtrl')
        if hasattr(control, 'GetValue'):
            self.voteShares = control.GetValue()
        else:
            self.voteShares = control.sr.edit.GetValue()
        return 1

    def OnSelectExpelVote(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('LabelTextTop', {'label': localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'),
         'text': self.memberName}))
        scrolllist.append(listentry.Get('Button', {'label': '',
         'caption': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Pick'),
         'OnClick': self.PickMember,
         'args': (None,)}))

    def PickMember(self, *args):
        memberslist = []
        for memberID in sm.GetService('corp').GetMemberIDsWithMoreThanAvgShares():
            who = cfg.eveowners.Get(memberID).ownerName
            memberslist.append([who, memberID, const.typeCharacterAmarr])

        res = uix.ListWnd(memberslist, 'character', localization.GetByLabel('UI/Corporations/Common/SelectCorpMember'), localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SelectMemberToExpel'), 1)
        if res:
            if session.charid == res[1]:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CannotExpelYourself')})
                return
            self.memberID = res[1]
            self.memberName = res[0]
            self.GoToStep(self.step, reload=1)

    def OnLeaveExpelVote(self, nextStep):
        if nextStep < self.step:
            return 1
        if self.memberID == 0:
            return 0
        return 1

    def OnSelectGeneralVote(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfOptions'),
         'setValue': self.voteOptionsCount,
         'name': 'voteOptionsCtrl',
         'intmode': (2, 50)}))

    def OnLeaveGeneralVote(self, nextStep):
        control = uiutil.GetChild(self, 'voteOptionsCtrl')
        if hasattr(control, 'GetValue'):
            self.voteOptionsCount = control.GetValue()
        else:
            self.voteOptionsCount = control.sr.edit.GetValue()
        return 1

    def OnSelectVoteOptions(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=0, cancel=1, next=1)
        i = 0
        while i < self.voteOptionsCount:
            i += 1
            title = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionText', option=i)
            identifier = 'voteOption%s' % i
            value = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/EnterTextForOption', option=i)
            if len(self.voteOptions) >= i:
                value = self.voteOptions[i - 1]
            scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
             'label': title,
             'setValue': value,
             'name': identifier,
             'maxLength': 100}))

    def OnLeaveVoteOptions(self, nextStep):
        self.voteOptions = []
        i = 0
        while i < self.voteOptionsCount:
            i += 1
            identifier = 'voteOption%s' % i
            entry = self.GetEntry(identifier)
            if not entry:
                continue
            value = entry.setValue.strip()
            if len(value) == 0:
                if nextStep < self.step:
                    continue
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionCannotBeMepty')})
                return 0
            self.voteOptions.append(value)

        return 1

    def GetEntry(self, identifier):
        for entry in self.sr.scroll.GetNodes():
            if entry.name == identifier:
                return entry

    def OnSelectVoteDetails(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'),
         'setValue': self.GetVoteTitle(),
         'name': 'voteTitleCtrl',
         'maxLength': 100}))
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'),
         'setValue': self.GetVoteDescription(),
         'name': 'voteDescriptionCtrl',
         'maxLength': 1000}))
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfDays'),
         'setValue': self.voteDays,
         'name': 'voteDaysCtrl',
         'intmode': (1, 30)}))

    def OnLeaveVoteDetails(self, nextStep):
        control = uiutil.GetChild(self, 'voteTitleCtrl')
        if hasattr(control, 'GetValue'):
            self.voteTitle = control.GetValue().strip()
        else:
            self.voteTitle = control.sr.edit.GetValue().strip()
        control = uiutil.GetChild(self, 'voteDescriptionCtrl')
        if hasattr(control, 'GetValue'):
            self.voteDescription = control.GetValue().strip()
        else:
            self.voteDescription = control.sr.edit.GetValue().strip()
        control = uiutil.GetChild(self, 'voteDaysCtrl')
        if hasattr(control, 'GetValue'):
            self.voteDays = control.GetValue()
        else:
            self.voteDays = control.sr.edit.GetValue()
        if nextStep < self.step:
            return 1
        if len(self.voteTitle) == 0:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintTitleCannotBeEmpty')})
            return 0
        if len(self.voteDescription) == 0:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HintDescriptionCannotBeMEmpty')})
            return 0
        return 1

    def OnSelectVoteSummary(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=1, cancel=1, next=0)
        for name, type in self.voteTypes:
            if type == self.voteType:
                scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Common/Type'),
                 'text': name}))

        if self.voteType == const.voteItemLockdown:
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Lockdown'),
             'text': cfg.invtypes.Get(self.typeID).typeName}))
        elif self.voteType == const.voteItemUnlock:
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Unlock'),
             'text': cfg.invtypes.Get(self.typeID).typeName}))
        elif self.voteType == const.voteShares:
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SharesToCreate'),
             'text': self.voteShares}))
        elif self.voteType == const.voteKickMember:
            scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/Common/ExpelCorpMember'),
             'text': self.memberName}))
        elif self.voteType == const.voteGeneral:
            i = 0
            while i < self.voteOptionsCount:
                i += 1
                title = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OptionText', option=i)
                value = self.voteOptions[i - 1]
                scrolllist.append(listentry.Get('LabelText', {'label': title,
                 'text': value}))

        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'),
         'text': self.voteTitle}))
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'),
         'text': self.voteDescription}))
        scrolllist.append(listentry.Get('LabelText', {'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NumberOfDays'),
         'text': self.voteDays}))

    def GetVoteTitle(self):
        if self.voteTitle is None:
            if self.voteType == const.voteShares:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CreateShares', shares=self.voteShares)
            elif self.voteType == const.voteItemLockdown:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockdownItem', item=self.typeID)
            elif self.voteType == const.voteItemUnlock:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/UnlockItem', item=self.typeID)
            elif self.voteType == const.voteKickMember:
                self.voteTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExpelFromCorporation', char=self.memberID)
            elif self.voteType == const.voteGeneral:
                self.voteTitle = ''
            else:
                log.LogError('Unknown Vote type')
        return self.voteTitle

    def GetVoteDescription(self):
        if self.voteDescription is None:
            self.voteDescription = ''
        return self.voteDescription

    def OnOK(self, *args):
        self.EnableNavigationButton(localization.GetByLabel('UI/Generic/OK'), False)
        SEC = 10000000L
        MIN = SEC * 60L
        HOUR = MIN * 60L
        hoursInADay = HOUR * 24
        options = util.Rowset(['optionText',
         'parameter',
         'parameter1',
         'parameter2'])
        now = blue.os.GetWallclockTime()
        endFileTime = long(self.voteDays * hoursInADay) + now
        if self.voteType == const.voteShares:
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CreateShares', shares=self.voteShares),
             self.voteShares,
             None,
             None])
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DoNotCreateShares'),
             0,
             None,
             None])
        elif self.voteType == const.voteItemLockdown:
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockdownItem', item=self.typeID),
             self.itemID,
             self.typeID,
             self.locationID])
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontLockdownItem', item=self.typeID),
             0,
             None,
             None])
        elif self.voteType == const.voteItemUnlock:
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/UnlockItem', item=self.typeID),
             self.itemID,
             self.typeID,
             self.locationID])
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontUnlockItem', item=self.typeID),
             0,
             None,
             None])
        elif self.voteType == const.voteKickMember:
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExpelFromCorporation', char=self.memberID),
             self.memberID,
             None,
             None])
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontExpelFromCorporation', memberName=self.memberName),
             0,
             None,
             None])
        elif self.voteType == const.voteGeneral:
            i = 0
            for each in self.voteOptions:
                options.lines.append([each,
                 i,
                 None,
                 None])
                i = i + 1

        else:
            log.LogError('Unknown Vote type')
            return
        sm.GetService('corp').InsertVoteCase(self.voteTitle, self.voteDescription, session.corpid, self.voteType, options, now, endFileTime)
        WizardDialogBase.OnOK(self, args)

    def OnComboChange(self, combo, header, value, *args):
        if combo.name == 'voteType':
            self.voteType = value
            self.InitVote()
        if combo.name == 'install_item_from':
            log.LogInfo('>OnComboChange self.step:', self.step)
            self.flagInput = value
            uthread.new(self.GoToStep, self.step, reload=1)

    def Confirm(self, *args):
        defaultBtns = uiutil.FindChildByClass(self, (uicls.ButtonCore,), ['trinity.Tr2Sprite2dContainer'], withAttributes=[('btn_default', 1)])
        for btn in defaultBtns:
            if btn.state == uiconst.UI_HIDDEN:
                continue
            activeFrame = btn.sr.defaultActiveFrame
            if activeFrame and activeFrame.state != uiconst.UI_HIDDEN:
                btn.OnClick()


class CorpVotes(uicls.Container):
    __guid__ = 'form.CorpVotes'
    __nonpersistvars__ = []

    def init(self):
        self.corpID = None
        self.isCorpPanel = 1
        self.sr.inited = 0
        self.sr.headers = [localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'), localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Started'), localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Ends')]

    def IAmAMemberOfThisCorp(self):
        return self.corpID == session.corpid

    def Load(self, args):
        if self.corpID is None:
            self.corpID = session.corpid
        if not self.sr.Get('inited', 0):
            self.state = uiconst.UI_HIDDEN
            self.sr.inited = 1
            btns = None
            buttonOptions = []
            self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            if self.IAmAMemberOfThisCorp() and session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                buttonOptions.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'),
                 self.ProposeVote,
                 (),
                 81])
            if self.IAmAMemberOfThisCorp() and session.charid != sm.GetService('corp').GetCorporation().ceoID:
                buttonOptions.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/RunForCEO'),
                 self.ProposeCEOVote,
                 (),
                 81])
            buttonOptions.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ClosedVotesShowAll'),
             self.ShowClosedVotes,
             (0,),
             81])
            if len(buttonOptions):
                btns = uicls.ButtonGroup(btns=buttonOptions, parent=self.toolbarContainer)
                self.toolbarContainer.height = btns.height
            else:
                self.toolbarContainer.state = uiconst.UI_HIDDEN
                self.toolbarContainer.height = 0
            self.sr.mainBtns = btns
            self.sr.scroll = uicls.Scroll(name='votes', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
            self.sr.tabs.Startup([[localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/OpenVotes'),
              self,
              self,
              'open'], [localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ClosedVotes'),
              self,
              self,
              'closed']], 'corporationvotes')
        if self.isCorpPanel:
            sm.GetService('corpui').LoadTop('ui_7_64_9', localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Votes'))
        self.state = uiconst.UI_PICKCHILDREN
        if args == 'open':
            self.ShowOpenVotes()
        elif args == 'closed':
            self.ShowClosedVotes()

    def OnCorporationVoteCaseChanged(self, corporationID, voteCaseID, change):
        log.LogInfo(self.__class__.__name__, 'OnCorporationVoteCaseChanged')
        if self is None or self.destroyed or not self.sr.inited:
            return
        if not self.ShouldVoteCaseBeCurrentlyVisible(corporationID, voteCaseID):
            return
        bAdd = True
        bRemove = True
        for old, new in change.itervalues():
            if old is not None:
                bAdd = False
            if new is not None:
                bRemove = False

        if bAdd and bRemove:
            raise RuntimeError('applications::OnCorporationApplicationChanged WTF')
        if 'endDateTime' is change and change['endDateTime'][1] is not None:
            if 'open' == self.sr.tabs.GetSelectedArgs():
                bRemove = True
        if bAdd:
            voteCases = sm.GetService('corp').GetVoteCasesByCorporation(self.corpID, 2)
            if not voteCases or 0 == len(voteCases):
                log.LogWarn('There are no vote cases to add??')
                return
            scrolllist = []
            voteCase = voteCases[voteCaseID]
            title = self.GetVoteText(voteCase)
            description = voteCase.description
            starts = util.FmtDate(voteCase.startDateTime, 'ls')
            ends = util.FmtDate(voteCase.endDateTime, 'ls')
            data = {'GetSubContent': self.GetOpenVoteSubContent,
             'label': title + '<t>' + starts + '<t>' + ends,
             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'): title.lower(),
             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'): description.lower(),
             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Started'): voteCase.startDateTime,
             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Ends'): voteCase.endDateTime,
             'groupItems': None,
             'id': ('corpopenvotes', voteCase.voteCaseID),
             'tabs': [],
             'state': 'locked',
             'vote': voteCase,
             'showicon': 'hide',
             'hint': description,
             'BlockOpenWindow': 1}
            scrolllist.append(listentry.Get('Group', data))
            if len(self.sr.scroll.sr.headers) > 0:
                self.sr.scroll.AddEntries(-1, scrolllist)
            else:
                self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.sr.headers)
            self.SetHint('')
        else:
            entry = self.GetEntryVoteCase(corporationID, voteCaseID)
            if entry is None:
                log.LogWarn('Remove/Update what? entry not found')
                return
            if bRemove:
                self.sr.scroll.RemoveEntries([entry])
            else:
                self.RefreshVotes()

    def OnCorporationVoteCaseOptionChanged(self, corporationID, voteCaseID, optionID, change):
        log.LogInfo(self.__class__.__name__, 'OnCorporationVoteCaseOptionChanged')
        if self is None or self.destroyed or not self.sr.inited:
            return
        self.ReloadVoteCaseSubContentIfVisible(corporationID, voteCaseID)

    def OnCorporationVoteChanged(self, corporationID, voteCaseID, characterID, change):
        log.LogInfo(self.__class__.__name__, 'OnCorporationVoteChanged')
        if self is None or self.destroyed or not self.sr.inited:
            return
        if characterID != session.charid:
            return
        self.ReloadVoteCaseSubContentIfVisible(corporationID, voteCaseID)

    def GetEntryVoteCase(self, corporationID, voteCaseID):
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if not entry.vote:
                continue
            if entry.vote.corporationID == corporationID and entry.vote.voteCaseID == voteCaseID:
                return entry

    def ShouldVoteCaseBeCurrentlyVisible(self, corporationID, voteCaseID):
        bVisible = 0
        if corporationID == self.corpID:
            selectedTab = self.sr.tabs.GetSelectedArgs()
            if selectedTab == 'open':
                votes = sm.GetService('corp').GetVoteCasesByCorporation(self.corpID, 2)
                if votes and len(votes):
                    bVisible = votes.has_key(voteCaseID)
            elif selectedTab == 'closed':
                votes = sm.GetService('corp').GetVoteCasesByCorporation(self.corpID, 1)
                if votes and len(votes):
                    bVisible = votes.has_key(voteCaseID)
        return bVisible

    def ReloadVoteCaseSubContentIfVisible(self, corporationID, voteCaseID):
        if not self.ShouldVoteCaseBeCurrentlyVisible(corporationID, voteCaseID):
            return
        entry = self.GetEntryVoteCase(corporationID, voteCaseID)
        if entry is None:
            log.LogWarn('Entry not found')
            return
        if entry.id:
            if entry.subEntries:
                rm = entry.subEntries
                entry.subEntries = []
                entry.open = 0
                self.sr.scroll.RemoveEntries(rm)
            if entry.GetSubContent and uicore.registry.GetListGroupOpenState(entry.id):
                subcontent = entry.GetSubContent(entry)
                if not len(subcontent):
                    subcontent.append(listentry.Get('Generic', {'label': localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem'),
                     'sublevel': entry.Get('sublevel', 0) + 1}))
                self.sr.scroll.AddEntries(entry.idx + 1, subcontent, entry)
                entry.open = 1
            if entry.panel and not entry.panel.destroyed:
                entry.panel.RefreshGroupWindow(0)

    def RefreshVotes(self):
        log.LogInfo(self.__class__.__name__, 'RefreshVotes')
        if self is None or self.destroyed or not self.sr.inited:
            log.LogInfo(self.__class__.__name__, 'RefreshVotes bad window state')
            return
        selectedTab = self.sr.tabs.GetSelectedArgs()
        if selectedTab == 'open':
            self.ShowOpenVotes()
        elif selectedTab == 'closed':
            self.ShowClosedVotes()

    def ShowOpenVotes(self, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            uix.HideButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ClosedVotesShowAll'))
            try:
                scrolllist = []
                if sm.GetService('corp').CanViewVotes(self.corpID):
                    votes = sm.GetService('corp').GetVoteCasesByCorporation(self.corpID, 2)
                    if votes and len(votes):
                        for vote in votes.itervalues():
                            title = self.GetVoteText(vote)
                            description = vote.description
                            starts = util.FmtDate(vote.startDateTime, 'ls')
                            ends = util.FmtDate(vote.endDateTime, 'ls')
                            data = {'GetSubContent': self.GetOpenVoteSubContent,
                             'label': title + '<t>' + starts + '<t>' + ends,
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'): title.lower(),
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'): description.lower(),
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Started'): vote.startDateTime,
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Ends'): vote.endDateTime,
                             'groupItems': None,
                             'id': ('corpopenvotes', vote.voteCaseID),
                             'tabs': [],
                             'state': 'locked',
                             'vote': vote,
                             'showicon': 'hide',
                             'hint': description,
                             'BlockOpenWindow': 1}
                            scrolllist.append(listentry.Get('Group', data))
                            uicore.registry.SetListGroupOpenState(('corpopenvotes', vote.voteCaseID), 0)

                else:
                    self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/AccessDeniedOnlyShareholders'))
                if len(scrolllist):
                    self.SetHint('')
                    self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.sr.headers)
                else:
                    self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist)
                    self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NoOpenVotes'))
            finally:
                sm.GetService('corpui').HideLoad()

        except:
            log.LogException()
            sys.exc_clear()

    def GetOpenVoteSubContent(self, nodedata, *args):
        try:
            scrolllist = []
            vote = nodedata.vote
            options = sm.GetService('corp').GetVoteCaseOptions(vote.voteCaseID, self.corpID)
            if len(options):
                charVotes = sm.GetService('corp').GetVotes(self.corpID, vote.voteCaseID)
                hasVoted = 0
                votedFor = -1
                if charVotes and charVotes.has_key(session.charid):
                    hasVoted = 1
                    votedFor = charVotes[session.charid].optionID
                canVote = sm.GetService('corp').CanVote(self.corpID)
                i = 0
                for option in options.itervalues():
                    i += 1
                    listentryType = ''
                    textEntryName = ''
                    text = self.GetVoteOptionText(option, vote)
                    dict = {}
                    if hasVoted or not canVote:
                        listentryType = 'Text'
                        textEntryName = 'text'
                        if option.optionID == votedFor:
                            dict[textEntryName] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteItemHasVoted', optionNumber=i, optionText=text)
                        else:
                            dict[textEntryName] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteItemCannotVote', optionNumber=i, optionText=text)
                    else:
                        listentryType = 'Button'
                        textEntryName = 'label'
                        dict['caption'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Vote')
                        dict['OnClick'] = self.InsertVote
                        dict['args'] = (self.corpID, vote.voteCaseID, option.optionID)
                        dict[textEntryName] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteItemCanVote', optionNumber=i, optionText=text)
                    dict['sublevel'] = 1
                    scrolllist.append(listentry.Get(listentryType, dict))

                dict = {'line': 1}
                for option in options.itervalues():
                    if not option.parameter:
                        continue
                    if vote.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                        dict['text'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/MoreInfoItemLocatedAtLocation', item=option.parameter1, loc=option.parameter2)
                        dict['itemID'] = option.parameter
                        dict['typeID'] = option.parameter1
                        dict['sublevel'] = 1
                        scrolllist.append(listentry.Get('Text', dict))

            return scrolllist
        except:
            log.LogException()
            sys.exc_clear()

    def ShowClosedVotes(self, maxLen = 20, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            uix.ShowButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ClosedVotesShowAll'))
            try:
                if maxLen > 0 or eve.Message('ConfirmShowAllClosedVotes', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                    votes = sm.GetService('corp').GetVoteCasesByCorporation(self.corpID, 1, maxLen)
                    scrolllist = []
                    if votes and len(votes):
                        for vote in votes.itervalues():
                            title = self.GetVoteText(vote)
                            description = vote.description
                            starts = util.FmtDate(vote.startDateTime, 'ls')
                            ends = util.FmtDate(vote.endDateTime, 'ls')
                            data = {'GetSubContent': self.GetClosedVoteSubContent,
                             'label': title + '<t>' + starts + '<t>' + ends,
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'): title.lower(),
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'): description.lower(),
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Started'): vote.startDateTime,
                             'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Ends'): vote.endDateTime,
                             'groupItems': None,
                             'id': ('corpclosedvotes', vote.voteCaseID),
                             'tabs': [],
                             'state': 'locked',
                             'vote': vote,
                             'showicon': 'hide',
                             'hint': description,
                             'BlockOpenWindow': 1}
                            scrolllist.append(listentry.Get('Group', data))
                            uicore.registry.SetListGroupOpenState(('corpclosedvotes', vote.voteCaseID), 0)
                            continue

                    if len(scrolllist):
                        self.SetHint('')
                        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.sr.headers)
                        self.sr.showAll = uicls.Checkbox(text='checkbox 1', parent=uicls.Container(), configName='checkbox', retval=None, checked=0, callback=self.OnCheckboxChange)
                    else:
                        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist)
                        self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/NoClosedVotes'))
            finally:
                sm.GetService('corpui').HideLoad()

        except:
            log.LogException()
            sys.exc_clear()

    def OnCheckboxChange(self, checkbox, *args):
        eve.Message(checkbox.checked)

    def GetClosedVoteSubContent(self, nodedata, *args):
        try:
            scrolllist = []
            vote = nodedata.vote
            options = sm.GetService('corp').GetVoteCaseOptions(vote.voteCaseID, self.corpID)
            if len(options):
                totalVotes = 0
                for option in options.itervalues():
                    totalVotes = totalVotes + option.votesFor

                for option in options.itervalues():
                    text = self.GetVoteOptionText(option, vote)
                    percent = 0
                    if totalVotes:
                        percent = option.votesFor / totalVotes * 100
                    voteInfo = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ClosedVoteResultColumn', percentage=percent, votesFor=option.votesFor, totalVotes=totalVotes)
                    scrolllist.append(listentry.Get('Text', {'text': '<t>'.join((text, voteInfo))}))

            if len(options):
                dict = {'line': 1}
                for option in options.itervalues():
                    if not option.parameter:
                        continue
                    if vote.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                        dict['text'] = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/MoreInfoItemLocatedAtLocation', item=option.parameter1, loc=option.parameter2)
                        dict['itemID'] = option.parameter
                        dict['typeID'] = option.parameter1
                        scrolllist.append(listentry.Get('Text', dict))

            return scrolllist
        except:
            log.LogException()
            sys.exc_clear()

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def InsertVote(self, corpID, voteCaseID, voteValue, sender, *args):
        oldState = None
        if sender is not None and hasattr(sender, 'state'):
            oldState = sender.state
            sender.state = uiconst.UI_DISABLED
        sm.GetService('corp').InsertVote(corpID, voteCaseID, voteValue)
        self.RefreshVotes()

    def ProposeVote(self, *args):
        local = sm.GetService('corp')
        if not (self.IAmAMemberOfThisCorp() and session.corprole & const.corpRoleDirector == const.corpRoleDirector):
            eve.Message('CrpOnlyDirectorsCanProposeVotes')
            return
        dlg = form.VoteWizardDialog.Open()
        dlg.ShowModal()

    def ProposeCEOVote(self, *args):
        local = sm.GetService('corp')
        if not (self.IAmAMemberOfThisCorp() and sm.GetService('corp').MemberCanRunForCEO()):
            eve.Message('CantRunForCEOAtTheMoment')
            return
        format = [{'type': 'btline'}]
        format.append({'type': 'checkbox',
         'setvalue': 1,
         'key': const.voteCEO,
         'group': 'votetype',
         'label': '_hide',
         'text': '_hide',
         'hidden': 1})
        format.append({'type': 'push',
         'frame': 1,
         'height': 6})
        format.append({'type': 'edit',
         'setvalue': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteMemberForCEO', char=session.charid),
         'key': 'title',
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Title'),
         'required': 1,
         'frame': 1,
         'maxlength': 500})
        format.append({'type': 'bbline'})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'description',
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Description'),
         'frame': 1,
         'maxLength': 100})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        format.append({'type': 'push'})
        format.append({'type': 'btline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'setvalue': 1,
         'intonly': [1, 5],
         'key': 'time',
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DaysToLive'),
         'frame': 1})
        format.append({'type': 'bbline'})
        retval = uix.HybridWnd(format, localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ProposeVote'), 1, None, uiconst.OKCANCEL, None, 320)
        if retval is not None:
            self.CreateVote(retval, self.corpID)

    def CreateVote(self, result, corporationID):
        SEC = 10000000L
        MIN = SEC * 60L
        HOUR = MIN * 60L
        hoursInADay = HOUR * 24
        voteCaseText = result['title']
        description = result['description']
        voteType = result['votetype']
        options = util.Rowset(['optionText',
         'parameter',
         'parameter1',
         'parameter2'])
        now = blue.os.GetWallclockTime()
        endFileTime = long(result['time'] * hoursInADay) + now
        if voteType == const.voteShares:
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CreateShares', shares=result['shares']),
             result['shares'],
             None,
             None])
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DoNotCreateShares'),
             0,
             None,
             None])
        elif voteType == const.voteKickMember:
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExpelFromCorporation', char=result['kickmember'][1]),
             result['kickmember'][1],
             None,
             None])
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontExpelFromCorporation', memberName=result['kickmember'][0]),
             0,
             None,
             None])
        elif voteType == const.voteGeneral:
            i = 0
            for each in result['options']:
                options.lines.append([each,
                 i,
                 None,
                 None])
                i = i + 1

        elif voteType == const.voteCEO:
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/SomeoneForCEO', char=session.charid),
             session.charid,
             None,
             None])
            options.lines.append([localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontChangeCEO'),
             0,
             None,
             None])
        else:
            log.LogError('Unknown Vote type')
            return
        sm.GetService('corp').InsertVoteCase(voteCaseText, description, corporationID, voteType, options, now, endFileTime)

    def ProposeVoteErrorCheck(self, ret):
        typeconst = ret['votetype']
        if typeconst == const.voteShares and ret['shares'] == 0:
            return localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HaveToSetAmountOfShares')
        if typeconst == const.voteKickMember and ret['kickmember'] is None:
            return localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/HaveToPickMember')
        if typeconst == const.voteGeneral and (ret['options'] is None or len(ret['options']) <= 1):
            return localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/Min2OptionsForVote')
        if typeconst == const.voteCEO:
            return ''
        return ''

    def GetVoteOptionText(self, option, vote):
        optionText = option.optionText
        if vote.voteType == const.voteShares:
            if option.optionID == 0:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/CreateShares', shares=option.parameter)
            else:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DoNotCreateShares')
        elif vote.voteType == const.voteWar:
            if option.optionID == 0:
                victimName = cfg.eveowners.Get(option.parameter).name
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DeclareWarAgainst', Name=victimName)
            else:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontDeclareWar')
        elif vote.voteType == const.voteItemLockdown:
            if option.optionID == 0:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/LockdownItem', item=option.parameter1)
            else:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontLockdownItem', item=option.parameter1)
        elif vote.voteType == const.voteItemUnlock:
            if option.optionID == 0:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/UnlockItem', item=option.parameter1)
            else:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontUnlockItem', item=option.parameter1)
        elif vote.voteType == const.voteKickMember:
            if option.optionID == 0:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/ExpelFromCorporation', char=option.parameter)
            else:
                optionText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/DontExpelCorporationMember')
        elif vote.voteType == const.voteGeneral:
            pass
        return optionText

    def GetVoteText(self, vote):
        voteText = vote.voteCaseText
        print 'getting vote text'
        if vote.voteType == const.voteShares:
            voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeCreateShares')
        elif vote.voteType == const.voteWar:
            voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeDeclareWar')
        elif vote.voteType == const.voteItemLockdown:
            voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeLockBlueprint')
        elif vote.voteType == const.voteItemUnlock:
            voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeUnlockBlueprint')
        elif vote.voteType == const.voteKickMember:
            voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeKickMember')
        elif vote.voteType == const.voteGeneral:
            voteText = localization.GetByLabel('UI/Corporations/CorporationWindow/Politics/VoteTypeGeneral')
        return voteText