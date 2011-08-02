import sys
import blue
import uthread
import util
import xtriui
import uix
import uiutil
import form
import listentry
import log
import uicls
import uiconst

class WizardDialogBase(uicls.Window):
    __guid__ = 'form.WizardDialogBase'

    def OnOK(self, *args):
        self.closedByOK = 1
        self.CloseX()



    def OnCancel(self, *args):
        self.CloseX()



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
                    (title, funcIn, funcOut,) = data
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
                (title, funcIn, funcOut,) = data
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
        buttonParams.append([mls.UI_CMD_OK,
         self.OnOK,
         (),
         66,
         0,
         1,
         0])
        buttonParams.append([mls.UI_CMD_BACK,
         self.OnBack,
         (),
         66])
        buttonParams.append([mls.UI_CMD_CANCEL,
         self.OnCancel,
         (),
         66])
        buttonParams.append([mls.UI_CMD_NEXT,
         self.OnNext,
         (),
         66,
         0,
         1,
         0])
        buttons = uicls.ButtonGroup(btns=buttonParams, parent=self.sr.main, idx=0)
        self.navigationBtns = buttons
        self.EnableNavigationButton(mls.UI_CMD_BACK, back)
        self.EnableNavigationButton(mls.UI_CMD_OK, ok)
        self.EnableNavigationButton(mls.UI_CMD_CANCEL, cancel)
        self.EnableNavigationButton(mls.UI_CMD_NEXT, next)



    def EnableNavigationButton(self, button, enabled):
        self.navigationBtns.GetBtnByLabel(button).state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][(not not enabled)]



    def SetSteps(self, steps, firstStep = None):
        log.LogInfo('SetSteps firstStep', firstStep)
        if firstStep is not None and not steps.has_key(firstStep):
            raise RuntimeError('SetSteps default step argument is invalid')
        self.steps = steps
        if firstStep is not None:
            self.GoToStep(firstStep)



    def SetHeading(self, heading):
        if self.heading is None:
            self.heading = uicls.CaptionLabel(text=heading, parent=self.sr.topParent, align=uiconst.CENTERLEFT, left=70, idx=0)
        else:
            self.heading.text = heading



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)




class VoteWizardDialog(WizardDialogBase):
    __guid__ = 'form.VoteWizardDialog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'station_inflight'
        self.heading = None
        self.step = 0
        self.navigationBtns = None
        self.voteTypes = [[mls.UI_CORP_CREATESHARES, const.voteShares]]
        if eve.session.allianceid is None:
            self.voteTypes.append([mls.UI_CMD_DECLAREWAR, const.voteWar])
        self.voteTypes.append([mls.UI_CMD_EXPELMEMBER, const.voteKickMember])
        self.voteTypes.append([mls.UI_CORP_GENERALVOTE, const.voteGeneral])
        if eve.session.stationid is not None:
            self.voteTypes.append([mls.UI_CORP_LOCKBLUEPRINT, const.voteItemLockdown])
            self.voteTypes.append([mls.UI_CORP_UNLOCKBLUEPRINT, const.voteItemUnlock])
        self.voteTypesDict = {}
        for (description, value,) in self.voteTypes:
            self.voteTypesDict[value] = description

        self.voteType = self.voteTypes[0][1]
        self.locationID = eve.session.stationid
        self.InitVote()
        steps = {1: (mls.UI_CORP_SELECTVOTETYPE, self.OnSelectVoteType, None),
         2: (mls.UI_CMD_DECLAREWAR, self.OnSelectWarVote, self.OnLeaveWarVote),
         3: (mls.UI_CORP_CREATESHARES, self.OnSelectShareVote, self.OnLeaveShareVote),
         4: (mls.UI_CMD_EXPELMEMBER, self.OnSelectExpelVote, self.OnLeaveExpelVote),
         5: (mls.UI_CORP_LOCKBLUEPRINT, self.OnSelectLockdownVote, self.OnLeaveLockdownVote),
         6: (mls.UI_CORP_UNLOCKBLUEPRINT, self.OnSelectUnlockVote, self.OnLeaveUnlockVote),
         7: (mls.UI_CORP_GENERALVOTE, self.OnSelectGeneralVote, self.OnLeaveGeneralVote),
         8: (mls.UI_CORP_VOTEOPS, self.OnSelectVoteOptions, self.OnLeaveVoteOptions),
         9: (mls.UI_CORP_VOTEDETAILS, self.OnSelectVoteDetails, self.OnLeaveVoteDetails),
         10: (mls.UI_CORP_VOTESUMMARY, self.OnSelectVoteSummary, None)}
        uix.Flush(self.sr.main)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        step = None
        if len(steps):
            step = 1
        self.SetSteps(steps, step)
        self.SetHeading(mls.UI_CORP_PROPOSEVOTE)
        self.SetCaption(mls.UI_CORP_PROPOSEVOTE)
        self.SetMinSize([400, 300])
        self.SetWndIcon('ui_7_64_9', mainTop=-2)
        self.SetTopparentHeight(58)
        return self



    def InitVote(self):
        self.ownerName = mls.UI_CORP_HINT56
        self.ownerID = 0
        self.voteTitle = None
        self.voteDescription = None
        self.voteDays = 1
        self.voteShares = 1
        self.memberID = 0
        self.memberName = mls.UI_CORP_HINT57
        self.voteOptions = []
        self.voteOptionsCount = 2
        self.itemID = 0
        self.typeID = 0
        self.flagInput = None



    def OnSelectVoteType(self, step, scrolllist):
        self.SetNavigationButtons(back=0, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('Combo', {'options': self.voteTypes,
         'label': mls.UI_CORP_SELECTVOTETYPE,
         'cfgName': 'voteType',
         'setValue': self.voteType,
         'OnChange': self.OnComboChange,
         'name': 'voteType'}))



    def LogCurrentVoteType(self):
        log.LogInfo('%s:' % mls.UI_CORP_CURRENTVOTETYPE, self.voteType, 'name:', self.voteTypesDict[self.voteType])



    def GetNextStep(self):
        log.LogInfo('GetNextStep>>')
        self.LogCurrentVoteType()
        log.LogInfo('current step:', self.step, 'detail:', self.steps[self.step])
        nextStep = None
        if self.step == 1:
            if self.voteType == const.voteWar:
                nextStep = 2
            elif self.voteType == const.voteShares:
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
            if self.voteType == const.voteWar:
                prevStep = 2
            elif self.voteType == const.voteShares:
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
            if eve.session.stationid is not None:
                lockedItems = sm.GetService('corp').GetLockedItemsByLocation(self.locationID)
            if len(lockedItems) == 0:
                scrolllist.append(listentry.Get('Header', {'label': mls.UI_CORP_HINT58}))
                log.LogInfo('No Corp Hangar available')
                return 
            hangarItems = self.GetHangarItemsToUse()
            options = []
            if hangarItems is not None:
                options = self.GetAvailableHangars()
            options.append((mls.UI_CORP_HINT59, const.flagHangarAll))
            default = None
            if hangarItems is None:
                log.LogInfo('No Corp Hangar available')
                self.flagInput = const.flagHangarAll
                default = const.flagHangarAll
            if len(options):
                log.LogInfo('No options')
                if self.flagInput is not None:
                    for (description, flag,) in options:
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
             'label': mls.UI_CORP_HINT60,
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




    def PopulateAllLockedItems(self, scrolllist):
        try:
            log.LogInfo('>PopulateAllLockedItems')
            if eve.session.stationid is None:
                return 
            lockedItems = sm.GetService('corp').GetLockedItemsByLocation(self.locationID)
            listentries = []
            hangarID = self.GetHangarLocationIDToUse()
            if hangarID is None:
                hangarID = eve.session.stationid
            blueprints = sm.RemoteSvc('factory').GetBlueprintInformationAtLocation(hangarID, 1)
            sanctionedActionsInEffect = sm.GetService('corp').GetSanctionedActionsByCorporation(eve.session.corpid, 1).itervalues()
            voteCases = sm.GetService('corp').GetVoteCasesByCorporation(eve.session.corpid, 2)
            sanctionedActionsByLockedItemID = util.IndexRowset(sanctionedActionsInEffect.header, [], 'parameter')
            if sanctionedActionsInEffect and len(sanctionedActionsInEffect):
                for sanctionedActionInEffect in sanctionedActionsInEffect:
                    if sanctionedActionInEffect.voteType in [const.voteItemLockdown] and sanctionedActionInEffect.parameter and sanctionedActionInEffect.inEffect:
                        sanctionedActionsByLockedItemID[sanctionedActionInEffect.parameter] = sanctionedActionInEffect.line

            voteCaseIDByItemToUnlockID = {}
            if voteCases and len(voteCases):
                for voteCase in voteCases.itervalues():
                    if voteCase.voteType in [const.voteItemUnlock] and voteCase.endDateTime > blue.os.GetTime() - DAY:
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
                if item.ownerID != eve.session.corpid:
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
                    itemTypeInfo = cfg.invtypes.Get(item.typeID)
                    description = itemTypeInfo.name
                    extraInfo = ''
                    if blueprint.copy == 1:
                        extraInfo = '%s,' % mls.UI_GENERIC_COPY
                        if blueprint.licensedProductionRunsRemaining == 0:
                            continue
                        if blueprint.licensedProductionRunsRemaining != -1:
                            extraInfo = '%s %s' % (extraInfo, mls.UI_CORP_LICENSEDRUNSREMAINING2 % {'runsRemaining': blueprint.licensedProductionRunsRemaining})
                        else:
                            extraInfo = '%s %s' % (extraInfo, mls.UI_CORP_LICENSEDRUNSREMAINING2 % {'runsRemaining': mls.UI_GENERIC_INFINITE})
                    if blueprint.productivityLevel:
                        if len(extraInfo):
                            extraInfo = extraInfo + ','
                        extraInfo = '%s %s' % (extraInfo, mls.UI_SHARED_PRODUCTIVITY2 % {'productivityLevel': blueprint.productivityLevel})
                    if blueprint.materialLevel:
                        if len(extraInfo):
                            extraInfo = extraInfo + ','
                        extraInfo = '%s %s' % (extraInfo, mls.UI_SHARED_MATERIALEFF2 % {'materialLevel': blueprint.materialLevel})
                    if extraInfo == '':
                        extraInfo = ' (' + extraInfo + ')'
                    data = {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': '%s %s%s' % (itemTypeInfo.name, uiutil.UpperCase(mls.UI_GENERIC_LOCKED), extraInfo),
                     'getIcon': 1,
                     'OnClick': self.ClickHangarItem}
                else:
                    data = {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': '%s %s' % (cfg.invtypes.Get(item.typeID).name, uiutil.UpperCase(mls.UI_GENERIC_LOCKED)),
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
            sanctionedActionsInEffect = sm.GetService('corp').GetSanctionedActionsByCorporation(eve.session.corpid, 1).itervalues()
            voteCases = sm.GetService('corp').GetVoteCasesByCorporation(eve.session.corpid, 2)
            sanctionedActionsByLockedItemID = util.IndexRowset(sanctionedActionsInEffect.header, [], 'parameter')
            if sanctionedActionsInEffect and len(sanctionedActionsInEffect):
                for sanctionedActionInEffect in sanctionedActionsInEffect:
                    if sanctionedActionInEffect.voteType in [const.voteItemLockdown] and sanctionedActionInEffect.parameter and sanctionedActionInEffect.inEffect:
                        sanctionedActionsByLockedItemID[sanctionedActionInEffect.parameter] = sanctionedActionInEffect.line

            voteCaseIDByItemToUnlockID = {}
            if voteCases and len(voteCases):
                for voteCase in voteCases.itervalues():
                    if voteCase.voteType in [const.voteItemUnlock] and voteCase.endDateTime > blue.os.GetTime() - DAY:
                        options = sm.GetService('corp').GetVoteCaseOptions(voteCase.voteCaseID, voteCase.corporationID)
                        if len(options):
                            for option in options.itervalues():
                                if option.parameter:
                                    voteCaseIDByItemToUnlockID[option.parameter] = voteCase.voteCaseID


            itemCount = len(hangarItems)
            for item in hangarItems:
                locked = sm.GetService('corp').IsItemLocked(item)
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
                    itemTypeInfo = cfg.invtypes.Get(item.typeID)
                    description = itemTypeInfo.name
                    extraInfo = ''
                    if blueprint.copy == 1:
                        extraInfo = '%s,' % mls.UI_GENERIC_COPY
                        if blueprint.licensedProductionRunsRemaining == 0:
                            continue
                        if blueprint.licensedProductionRunsRemaining != -1:
                            extraInfo = '%s %s' % (extraInfo, mls.UI_CORP_LICENSEDRUNSREMAINING2 % {'runsRemaining': blueprint.licensedProductionRunsRemaining})
                        else:
                            extraInfo = '%s %s' % (extraInfo, mls.UI_CORP_LICENSEDRUNSREMAINING2 % {'runsRemaining': mls.UI_GENERIC_INFINITE})
                    if blueprint.productivityLevel:
                        if len(extraInfo):
                            extraInfo = extraInfo + ','
                        extraInfo = '%s %s' % (extraInfo, mls.UI_SHARED_PRODUCTIVITY2 % {'productivityLevel': blueprint.productivityLevel})
                    if blueprint.materialLevel:
                        if len(extraInfo):
                            extraInfo = extraInfo + ','
                        extraInfo = '%s %s' % (extraInfo, mls.UI_SHARED_MATERIALEFF2 % {'materialLevel': blueprint.materialLevel})
                    if extraInfo != '':
                        extraInfo = ' (' + extraInfo + ')'
                    data = {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': '%s %s[%s]%s' % (itemTypeInfo.name,
                               ['', mls.UI_GENERIC_LOCKED + ' '][(not not locked)],
                               item.stacksize,
                               extraInfo),
                     'getIcon': 1,
                     'OnClick': self.ClickHangarItem}
                else:
                    data = {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': '%s %s[%s]' % (cfg.invtypes.Get(item.typeID).name, ['', mls.UI_GENERIC_LOCKED + ' '][(not not locked)], item.stacksize),
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
                scrolllist.append(listentry.Get('Header', {'label': mls.UI_CORP_HINT61}))
                log.LogInfo('No Corp Hangar available')
                return 
            default = None
            if self.flagInput is not None:
                for (description, flag,) in options:
                    if self.flagInput == flag:
                        default = flag
                        break

            label = mls.UI_CORP_HINT62
            data = {'options': options,
             'label': label,
             'cfgName': 'install_item_from',
             'setValue': default,
             'OnChange': self.OnComboChange,
             'name': 'install_item_from'}
            scrolllist.append(listentry.Get('Header', {'label': mls.UI_CORP_HINT63}))
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
                    if eve.session.corprole & param[1] != param[1]:
                        continue
                if canTake:
                    if eve.session.corprole & param[2] != param[2]:
                        continue
                hangarDescription = divisions[i]
                options.append((hangarDescription, param[0]))

            return options

        finally:
            log.LogInfo('<GetAvailableHangars')




    def GetHangarItemsToUse(self, flagID = None):
        try:
            log.LogInfo('>GetHangarItemsToUse')
            listing = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, self.locationID, 'offices')
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
            office = None
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
                extraInfo = ''
                if blueprint.copy == 1:
                    extraInfo = '%s,' % mls.UI_GENERIC_COPY
                    if blueprint.licensedProductionRunsRemaining == 0:
                        continue
                    if blueprint.licensedProductionRunsRemaining != -1:
                        extraInfo = '%s %s' % (extraInfo, mls.UI_CORP_LICENSEDRUNSREMAINING2 % {'runsRemaining': blueprint.licensedProductionRunsRemaining})
                    else:
                        extraInfo = '%s %s' % (extraInfo, mls.UI_CORP_LICENSEDRUNSREMAINING2 % {'runsRemaining': mls.UI_GENERIC_INFINITE})
                if blueprint.productivityLevel:
                    if len(extraInfo):
                        extraInfo = extraInfo + ','
                    extraInfo = '%s %s' % (extraInfo, mls.UI_SHARED_PRODUCTIVITY2 % {'productivityLevel': blueprint.productivityLevel})
                if blueprint.materialLevel:
                    if len(extraInfo):
                        extraInfo = extraInfo + ','
                    extraInfo = '%s %s' % (extraInfo, mls.UI_SHARED_MATERIALEFF2 % {'materialLevel': blueprint.materialLevel})
                item = None
                for hangarItem in hangarItems:
                    if hangarItem.itemID == blueprint.itemID:
                        item = hangarItem
                        break

                if item is None:
                    log.LogInfo('Someone nabbed', blueprint.itemID, 'while I was looking for it.')
                    continue
                locked = sm.GetService('corp').IsItemLocked(item)
                if extraInfo != '':
                    extraInfo = ' (' + extraInfo + ')'
                data = {'info': item,
                 'itemID': item.itemID,
                 'typeID': item.typeID,
                 'label': '%s %s[%s]%s' % (itemTypeInfo.name,
                           ['', mls.UI_GENERIC_LOCKED + ' '][(not not locked)],
                           item.stacksize,
                           extraInfo),
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



    def OnSelectWarVote(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('LabelTextTop', {'label': mls.UI_CORP_DECLAREWARAGAINST,
         'text': self.ownerName}))
        scrolllist.append(listentry.Get('Button', {'label': '',
         'caption': mls.UI_CMD_PICK,
         'OnClick': self.PickCorporationOrAlliance,
         'args': (None,)}))



    def PickCorporationOrAlliance(self, *args):
        dlg = sm.GetService('window').GetWindow('CorporationOrAlliancePickerDailog', create=1, decoClass=form.CorporationOrAlliancePickerDailog, warableEntitysOnly=True)
        dlg.ShowModal()
        if dlg.ownerID:
            if dlg.ownerID in [eve.session.corpid, eve.session.allianceid]:
                eve.Message('CustomInfo', {'info': mls.UI_CORP_HINT64})
                return 
            self.ownerID = dlg.ownerID
            self.ownerName = cfg.eveowners.Get(self.ownerID).ownerName
            self.GoToStep(self.step, reload=1)



    def OnLeaveWarVote(self, nextStep):
        if self.ownerID == 0:
            if nextStep == 1:
                return 1
            return 0
        return 1



    def OnSelectShareVote(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=0, cancel=1, next=1)
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': mls.UI_CORP_NUMBEROFSHARES,
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
        scrolllist.append(listentry.Get('LabelTextTop', {'label': mls.UI_CORP_EXPEL,
         'text': self.memberName}))
        scrolllist.append(listentry.Get('Button', {'label': '',
         'caption': mls.UI_CMD_PICK,
         'OnClick': self.PickMember,
         'args': (None,)}))



    def PickMember(self, *args):
        memberslist = []
        for memberID in sm.GetService('corp').GetMemberIDsWithMoreThanAvgShares():
            who = cfg.eveowners.Get(memberID).ownerName
            memberslist.append([who, memberID, const.typeCharacterAmarr])

        res = uix.ListWnd(memberslist, 'character', mls.UI_CORP_SELECTMEMBER, mls.UI_CORP_HINT65, 1)
        if res:
            if eve.session.charid == res[1]:
                eve.Message('CustomInfo', {'info': mls.UI_CORP_HINT66})
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
         'label': mls.UI_CORP_NUMBEROFOPTIONS,
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
            title = '%s %s' % (mls.UI_CORP_OPTIONTEXT, i)
            identifier = 'voteOption%s' % i
            value = mls.UI_CORP_HINT67 % {'num': i}
            if len(self.voteOptions) >= i:
                value = self.voteOptions[(i - 1)]
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
                eve.Message('CustomInfo', {'info': mls.UI_CORP_HINT68})
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
         'label': mls.UI_GENERIC_TITLE,
         'setValue': self.GetVoteTitle(),
         'name': 'voteTitleCtrl',
         'maxLength': 100}))
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': mls.UI_GENERIC_DESCRIPTION,
         'setValue': self.GetVoteDescription(),
         'name': 'voteDescriptionCtrl',
         'maxLength': 1000}))
        scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
         'label': mls.UI_CORP_NUMBEROFDAYS,
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
            eve.Message('CustomInfo', {'info': mls.UI_CORP_HINT69})
            return 0
        if len(self.voteDescription) == 0:
            eve.Message('CustomInfo', {'info': mls.UI_CORP_HINT70})
            return 0
        return 1



    def OnSelectVoteSummary(self, step, scrolllist):
        self.SetNavigationButtons(back=1, ok=1, cancel=1, next=0)
        for (name, type,) in self.voteTypes:
            if type == self.voteType:
                scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_GENERIC_TYPE,
                 'text': name}))

        if self.voteType == const.voteWar:
            scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_CORP_AGAINST,
             'text': self.ownerName}))
            cost = sm.GetService('war').GetCostOfWarAgainst(self.ownerID)
            text = mls.UI_CORP_HINT71 % {'cost': util.FmtISK(cost)}
            scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_CORP_CURRENTCOST,
             'text': text}))
        elif self.voteType == const.voteItemLockdown:
            scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_CORP_LOCKDOWN,
             'text': cfg.invtypes.Get(self.typeID).typeName}))
        elif self.voteType == const.voteItemUnlock:
            scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_CORP_UNLOCK,
             'text': cfg.invtypes.Get(self.typeID).typeName}))
        elif self.voteType == const.voteShares:
            scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_CORP_SHARESTOCREATE,
             'text': self.voteShares}))
        elif self.voteType == const.voteKickMember:
            scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_CORP_EXPEL,
             'text': self.memberName}))
        elif self.voteType == const.voteGeneral:
            i = 0
            while i < self.voteOptionsCount:
                i += 1
                title = '%s %s' % (mls.UI_CORP_OPTIONTEXT, i)
                value = self.voteOptions[(i - 1)]
                scrolllist.append(listentry.Get('LabelText', {'label': title,
                 'text': value}))

        scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_GENERIC_TITLE,
         'text': self.voteTitle}))
        scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_GENERIC_DESCRIPTION,
         'text': self.voteDescription}))
        scrolllist.append(listentry.Get('LabelText', {'label': mls.UI_CORP_NUMBEROFDAYS,
         'text': self.voteDays}))



    def GetVoteTitle(self):
        if self.voteTitle is None:
            if self.voteType == const.voteShares:
                self.voteTitle = mls.UI_CORP_CREATESOMESHARES % {'what': self.voteShares}
            elif self.voteType == const.voteWar:
                self.voteTitle = '%s %s' % (mls.UI_CORP_DECLAREWARAGAINST, self.ownerName)
            elif self.voteType == const.voteItemLockdown:
                self.voteTitle = '%s %s' % (mls.UI_CORP_LOCKDOWNTHE, cfg.invtypes.Get(self.typeID).typeName)
            elif self.voteType == const.voteItemUnlock:
                self.voteTitle = '%s %s' % (mls.UI_CORP_UNLOCKTHE, cfg.invtypes.Get(self.typeID).typeName)
            elif self.voteType == const.voteKickMember:
                self.voteTitle = mls.UI_CORP_EXPELSOMEONEFROMCORP % {'who': self.memberName}
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
        self.EnableNavigationButton(mls.UI_CMD_OK, False)
        SEC = 10000000L
        MIN = SEC * 60L
        HOUR = MIN * 60L
        hoursInADay = HOUR * 24
        options = util.Rowset(['optionText',
         'parameter',
         'parameter1',
         'parameter2'])
        now = blue.os.GetTime()
        endFileTime = long(self.voteDays * hoursInADay) + now
        if self.voteType == const.voteShares:
            options.lines.append([mls.UI_CORP_CREATESOMESHARES % {'what': self.voteShares},
             self.voteShares,
             None,
             None])
            options.lines.append([mls.UI_CORP_DONOTCREATESHARES,
             0,
             None,
             None])
        elif self.voteType == const.voteWar:
            options.lines.append(['%s %s' % (mls.UI_CORP_DECLAREWARAGAINST, self.ownerName),
             self.ownerID,
             None,
             None])
            options.lines.append([mls.UI_CORP_CONTDECLAREWAR,
             0,
             None,
             None])
        elif self.voteType == const.voteItemLockdown:
            options.lines.append(['%s %s' % (mls.UI_CORP_LOCKDOWNTHE, cfg.invtypes.Get(self.typeID).typeName),
             self.itemID,
             self.typeID,
             self.locationID])
            options.lines.append(['%s %s' % (mls.UI_CORP_DONTLOCKDOWNTHE, cfg.invtypes.Get(self.typeID).typeName),
             0,
             None,
             None])
        elif self.voteType == const.voteItemUnlock:
            options.lines.append(['%s %s' % (mls.UI_CORP_UNLOCKTHE, cfg.invtypes.Get(self.typeID).typeName),
             self.itemID,
             self.typeID,
             self.locationID])
            options.lines.append(['%s %s' % (mls.UI_CORP_DONTUNLOCKTHE, cfg.invtypes.Get(self.typeID).typeName),
             0,
             None,
             None])
        elif self.voteType == const.voteKickMember:
            options.lines.append([mls.UI_CORP_EXPELSOMEONEFROMCORP % {'who': self.memberName},
             self.memberID,
             None,
             None])
            options.lines.append([mls.UI_CORP_DONTEXPELSOMEONEFROMCORP % {'who': self.memberName},
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
        sm.GetService('corp').InsertVoteCase(self.voteTitle, self.voteDescription, eve.session.corpid, self.voteType, options, now, endFileTime)
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
        self.sr.headers = [mls.UI_GENERIC_TITLE, mls.UI_GENERIC_STARTED, mls.UI_GENERIC_ENDS]



    def IAmAMemberOfThisCorp(self):
        return self.corpID == eve.session.corpid



    def Load(self, args):
        if self.corpID is None:
            self.corpID = eve.session.corpid
        if not self.sr.Get('inited', 0):
            self.state = uiconst.UI_HIDDEN
            self.sr.inited = 1
            btns = None
            buttonOptions = []
            self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            if self.IAmAMemberOfThisCorp() and eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                buttonOptions.append([mls.UI_CORP_PROPOSEVOTE,
                 self.ProposeVote,
                 (),
                 81])
            if self.IAmAMemberOfThisCorp() and eve.session.charid != sm.GetService('corp').GetCorporation().ceoID:
                buttonOptions.append([mls.UI_CORP_RUNFORCEO,
                 self.ProposeCEOVote,
                 (),
                 81])
            buttonOptions.append([mls.UI_CORP_CLOSEDVOTES_SHOWALL,
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
            self.sr.tabs.Startup([[mls.UI_CORP_OPENVOTES,
              self,
              self,
              'open'], [mls.UI_CORP_CLOSEDVOTES,
              self,
              self,
              'closed']], 'corporationvotes')
        if self.isCorpPanel:
            sm.GetService('corpui').LoadTop('ui_7_64_9', mls.UI_CORP_VOTES)
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
        for (old, new,) in change.itervalues():
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
            title = voteCase.voteCaseText
            description = voteCase.description
            starts = util.FmtDate(voteCase.startDateTime, 'ls')
            ends = util.FmtDate(voteCase.endDateTime, 'ls')
            data = {'GetSubContent': self.GetOpenVoteSubContent,
             'label': '%s<t>%s<t>%s' % (title, starts, ends),
             'sort_%s' % mls.UI_GENERIC_TITLE: title.lower(),
             'sort_%s' % mls.UI_GENERIC_DESCRIPTION: description.lower(),
             'sort_%s' % mls.UI_GENERIC_STARTED: voteCase.startDateTime,
             'sort_%s' % mls.UI_GENERIC_ENDS: voteCase.endDateTime,
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
        if characterID != eve.session.charid:
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
                    subcontent.append(listentry.Get('Generic', {'label': mls.UI_GENERIC_NOITEM,
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
            uix.HideButtonFromGroup(self.sr.mainBtns, mls.UI_CORP_CLOSEDVOTES_SHOWALL)
            try:
                scrolllist = []
                if sm.GetService('corp').CanViewVotes(self.corpID):
                    votes = sm.GetService('corp').GetVoteCasesByCorporation(self.corpID, 2)
                    if votes and len(votes):
                        for vote in votes.itervalues():
                            title = vote.voteCaseText
                            description = vote.description
                            starts = util.FmtDate(vote.startDateTime, 'ls')
                            ends = util.FmtDate(vote.endDateTime, 'ls')
                            data = {'GetSubContent': self.GetOpenVoteSubContent,
                             'label': '%s<t>%s<t>%s' % (title, starts, ends),
                             'sort_%s' % mls.UI_GENERIC_TITLE: title.lower(),
                             'sort_%s' % mls.UI_GENERIC_DESCRIPTION: description.lower(),
                             'sort_%s' % mls.UI_GENERIC_STARTED: vote.startDateTime,
                             'sort_%s' % mls.UI_GENERIC_ENDS: vote.endDateTime,
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
                    self.SetHint(mls.UI_CORP_ACCESSDENIED10)
                if len(scrolllist):
                    self.SetHint('')
                    self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.sr.headers)
                else:
                    self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist)
                    self.SetHint(mls.UI_CORP_NOOPENVOTES)

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
                if charVotes and charVotes.has_key(eve.session.charid):
                    hasVoted = 1
                    votedFor = charVotes[eve.session.charid].optionID
                canVote = sm.GetService('corp').CanVote(self.corpID)
                i = 0
                for option in options.itervalues():
                    i += 1
                    listentryType = ''
                    textEntryName = ''
                    text = ''
                    textpre = ''
                    dict = {}
                    if hasVoted or not canVote:
                        listentryType = 'Text'
                        textEntryName = 'text'
                        text = option.optionText
                        if option.optionID == votedFor:
                            textpre = ' ' + mls.UI_SHARED_YOURVOTE
                    else:
                        listentryType = 'Button'
                        textEntryName = 'label'
                        text = option.optionText
                        dict['caption'] = mls.UI_CORP_VOTE
                        dict['OnClick'] = self.InsertVote
                        dict['args'] = (self.corpID, vote.voteCaseID, option.optionID)
                    dict[textEntryName] = '  %s [%s]%s, %s<t><t>' % (mls.UI_CORP_OPTION,
                     i,
                     textpre,
                     text)
                    scrolllist.append(listentry.Get(listentryType, dict))

            if len(options):
                dict = {'line': 1}
                for option in options.itervalues():
                    if not option.parameter:
                        continue
                    if vote.voteType in [const.voteWar, const.voteKickMember, const.voteCEO]:
                        owner = cfg.eveowners.Get(option.parameter)
                        dict['text'] = '  %s, ' % mls.UI_GENERIC_MOREINFO + owner.ownerName
                        dict['itemID'] = option.parameter
                        dict['typeID'] = owner.typeID
                        scrolllist.append(listentry.Get('Text', dict))
                    elif vote.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                        locationText = mls.UI_SHARED_SOMETHINGATSOMEWHERE % {'typeName': cfg.invtypes.Get(option.parameter1).typeName,
                         'location': cfg.evelocations.Get(option.parameter2).locationName}
                        dict['text'] = '  %s, %s' % (mls.UI_GENERIC_MOREINFO, locationText)
                        dict['itemID'] = option.parameter
                        dict['typeID'] = option.parameter1
                        scrolllist.append(listentry.Get('Text', dict))

            return scrolllist
        except:
            log.LogException()
            sys.exc_clear()



    def ShowClosedVotes(self, maxLen = 20, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            uix.ShowButtonFromGroup(self.sr.mainBtns, mls.UI_CORP_CLOSEDVOTES_SHOWALL)
            try:
                if maxLen > 0 or eve.Message('ConfirmShowAllClosedVotes', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                    votes = sm.GetService('corp').GetVoteCasesByCorporation(self.corpID, 1, maxLen)
                    scrolllist = []
                    if votes and len(votes):
                        for vote in votes.itervalues():
                            title = vote.voteCaseText
                            description = vote.description
                            starts = util.FmtDate(vote.startDateTime, 'ls')
                            ends = util.FmtDate(vote.endDateTime, 'ls')
                            data = {'GetSubContent': self.GetClosedVoteSubContent,
                             'label': '%s<t>%s<t>%s' % (title, starts, ends),
                             'sort_%s' % mls.UI_GENERIC_TITLE: title.lower(),
                             'sort_%s' % mls.UI_GENERIC_DESCRIPTION: description.lower(),
                             'sort_%s' % mls.UI_GENERIC_STARTED: vote.startDateTime,
                             'sort_%s' % mls.UI_GENERIC_ENDS: vote.endDateTime,
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
                        self.SetHint(mls.UI_CORP_NOCLOSEDVOTES)

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
                    text = option.optionText
                    percent = 0
                    if totalVotes:
                        percent = option.votesFor / totalVotes * 100
                    scrolllist.append(listentry.Get('Text', {'text': '%s<t>%s %% (%s/%s)' % (text,
                              percent,
                              option.votesFor,
                              totalVotes)}))

            if len(options):
                dict = {'line': 1}
                for option in options.itervalues():
                    if not option.parameter:
                        continue
                    if vote.voteType in [const.voteWar, const.voteKickMember, const.voteCEO]:
                        owner = cfg.eveowners.Get(option.parameter)
                        dict['text'] = '  %s<t>' % mls.UI_GENERIC_MOREINFO + owner.ownerName
                        dict['itemID'] = option.parameter
                        dict['typeID'] = owner.typeID
                        scrolllist.append(listentry.Get('Text', dict))
                    elif vote.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                        locationText = mls.UI_SHARED_LOCATEDATSOMEWHERE % {'location': cfg.evelocations.Get(option.parameter2).locationName}
                        dict['text'] = '  %s<t>%s<t>%s' % (mls.UI_GENERIC_MOREINFO, cfg.invtypes.Get(option.parameter1).typeName, locationText)
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
        if not (self.IAmAMemberOfThisCorp() and eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector):
            eve.Message('CrpOnlyDirectorsCanProposeVotes')
            return 
        dlg = sm.GetService('window').GetWindow('VoteWizardDialog', create=1)
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
         'setvalue': mls.UI_CORP_VOTESOMEONEFORCEO % {'who': cfg.eveowners.Get(eve.session.charid).name},
         'key': 'title',
         'label': mls.UI_GENERIC_TITLE,
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
         'label': mls.UI_GENERIC_DESCRIPTION,
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
         'label': mls.UI_CORP_DAYSTOLIVE,
         'frame': 1})
        format.append({'type': 'bbline'})
        retval = uix.HybridWnd(format, mls.UI_CORP_PROPOSEVOTE, 1, None, uiconst.OKCANCEL, None, 320)
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
        now = blue.os.GetTime()
        endFileTime = long(result['time'] * hoursInADay) + now
        if voteType == const.voteShares:
            options.lines.append([mls.UI_CORP_CREATESOMESHARES % {'what': result['shares']},
             result['shares'],
             None,
             None])
            options.lines.append([mls.UI_CORP_DONOTCREATESHARES,
             0,
             None,
             None])
        elif voteType == const.voteWar:
            options.lines.append(['%s %s' % (mls.UI_CORP_DECLAREWARAGAINST, result['corpwar'][0]),
             result['corpwar'][1],
             None,
             None])
            options.lines.append([mls.UI_CORP_CONTDECLAREWAR,
             0,
             None,
             None])
        elif voteType == const.voteKickMember:
            options.lines.append([mls.UI_CORP_EXPELSOMEONEFROMCORP % {'who': result['kickmember'][0]},
             result['kickmember'][1],
             None,
             None])
            options.lines.append([mls.UI_CORP_DONTEXPELSOMEONEFROMCORP % {'who': result['kickmember'][0]},
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
            options.lines.append([mls.UI_CORP_SOMEONEFORCEO % {'who': cfg.eveowners.Get(eve.session.charid).name},
             eve.session.charid,
             None,
             None])
            options.lines.append([mls.UI_CORP_DONTCHANGECEO,
             0,
             None,
             None])
        else:
            log.LogError('Unknown Vote type')
            return 
        sm.GetService('corp').InsertVoteCase(voteCaseText, description, corporationID, voteType, options, now, endFileTime)



    def ProposeVoteErrorCheck(self, ret):
        typeconst = ret['votetype']
        if typeconst == const.voteWar and ret['corpwar'] is None:
            return mls.UI_CORP_HINT72
        if typeconst == const.voteShares and ret['shares'] == 0:
            return mls.UI_CORP_HINT73
        if typeconst == const.voteKickMember and ret['kickmember'] is None:
            return mls.UI_CORP_HINT74
        if typeconst == const.voteGeneral and (ret['options'] is None or len(ret['options']) <= 1):
            return mls.UI_CORP_HINT75
        if typeconst == const.voteCEO:
            return ''
        return ''




