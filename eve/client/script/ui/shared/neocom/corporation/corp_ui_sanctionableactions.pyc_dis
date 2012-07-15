#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/corporation/corp_ui_sanctionableactions.py
import sys
import blue
import util
import uix
import listentry
import log
import uicls
import uiconst
import localization

class CorpSanctionableActions(uicls.Container):
    __guid__ = 'form.CorpSanctionableActions'
    __nonpersistvars__ = []

    def init(self):
        self.sr.inited = 0

    def Load(self, args):
        self.voteTypes = {const.voteCEO: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NewCEO'),
         const.voteWar: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/DeclarationOfWar'),
         const.voteShares: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/CreationOfShares'),
         const.voteKickMember: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Expulsion'),
         const.voteGeneral: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/GeneralVote'),
         const.voteItemUnlock: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/UnlockBlueprint'),
         const.voteItemLockdown: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/LockBlueprint')}
        self.headers = [localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Type'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Title'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Description'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Expires'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ActedUpon'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/InEffect'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Rescinded')]
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            buttonOptions = [[localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ShowAll'),
              self.ShowSanctionableActionsNotInEffect,
              True,
              81]]
            btns = uicls.ButtonGroup(btns=buttonOptions, parent=self.toolbarContainer)
            self.toolbarContainer.height = btns.height
            self.sr.mainBtns = btns
            self.sr.scroll = uicls.Scroll(name='sanctionableactions', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
            self.sr.tabs.Startup([[localization.GetByLabel('UI/Corporations/CorpSanctionableActions/InEffect'),
              self,
              self,
              'ineffect'], [localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NotInEffect'),
              self,
              self,
              'notineffect']], 'corpsanctionableact')
        sm.GetService('corpui').LoadTop('ui_7_64_5', localization.GetByLabel('UI/Corporations/CorpSanctionableActions/SanctionableActions'))
        if args == 'ineffect':
            self.ShowSanctionableActionsInEffect()
        elif args == 'notineffect':
            self.ShowSanctionableActionsNotInEffect()

    def Refresh(self):
        if self is None or self.destroyed or not self.sr.inited:
            return
        selectedTab = self.sr.tabs.GetSelectedArgs()
        if selectedTab == 'ineffect':
            self.ShowSanctionableActionsInEffect()
        elif selectedTab == 'notineffect':
            self.ShowSanctionableActionsNotInEffect()

    def OnSanctionedActionChanged(self, corpID, voteCaseID, change):
        self.Refresh()

    def ShowSanctionableActionsInEffect(self, *args):
        try:
            try:
                sm.GetService('corpui').ShowLoad()
                uix.HideButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ShowAll'))
                scrolllist = []
                self.sr.scroll.Clear()
                if not sm.GetService('corp').CanViewVotes(eve.session.corpid):
                    self.SetHint(localization.GetByLabel('UI/Corporations/AccessRestrictions/MustBeCEODirectorOrShareholder'))
                    return
                voteCases = {k:v for k, v in sm.GetService('corp').GetVoteCasesByCorporation(eve.session.corpid).iteritems()}
                rows = sm.GetService('corp').GetSanctionedActionsByCorporation(eve.session.corpid, 1)
                if rows is not None:
                    owners = []
                    for row in rows.itervalues():
                        if row.voteType in [const.voteCEO, const.voteWar, const.voteKickMember] and row.parameter:
                            if row.parameter not in owners:
                                owners.append(row.parameter)

                    if len(owners):
                        cfg.eveowners.Prime(owners)
                    for row in rows.itervalues():
                        if row.voteType in [const.voteItemUnlock,
                         const.voteCEO,
                         const.voteWar,
                         const.voteShares,
                         const.voteKickMember,
                         const.voteItemLockdown] and row.parameter == 0:
                            continue
                        voteType = self.voteTypes[row.voteType]
                        title = voteCases[row.voteCaseID].voteCaseText.split('<br>')[0]
                        description = voteCases[row.voteCaseID].description.split('<br>')[0]
                        expires = util.FmtDate(row.expires)
                        actedUpon = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.actedUpon]
                        inEffect = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.inEffect]
                        rescended = localization.GetByLabel('UI/Generic/No')
                        if row.timeRescended:
                            rescended = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=rescended, timestamp=util.FmtDate(row.timeRescended))
                        if row.timeActedUpon:
                            actedUpon = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=actedUpon, timestamp=util.FmtDate(row.timeActedUpon))
                        label = '<t>'.join((voteType,
                         title,
                         description,
                         expires,
                         actedUpon,
                         inEffect,
                         rescended))
                        data = {'GetSubContent': self.GetInEffectSanctionedActionSubContent,
                         'label': label,
                         'groupItems': None,
                         'id': ('corpsaie', row.voteCaseID),
                         'tabs': [],
                         'state': 'locked',
                         'row': row,
                         'voteCases': voteCases,
                         'showicon': 'hide',
                         'BlockOpenWindow': 1}
                        scrolllist.append(listentry.Get('Group', data))
                        uicore.registry.SetListGroupOpenState(('corpsaie', row.voteCaseID), 0)

                self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.headers, noContentHint=localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NoSanctionableActionsInEffect'))
            finally:
                sm.GetService('corpui').HideLoad()

        except:
            log.LogException()
            sys.exc_clear()

    def GetInEffectSanctionedActionSubContent(self, nodedata, *args):
        try:
            row = nodedata.row
            voteCases = nodedata.voteCases
            if row.voteType == const.voteGeneral:
                fields = {}
                voteCaseOptions = {}
                for option in sm.GetService('corp').GetVoteCaseOptions(row.voteCaseID):
                    voteCaseOptions[option.optionID] = option

                fields['Decision'] = voteCaseOptions[row.optionID].optionText
                return self.AddSanctionableEntry([fields, None])
            scrolllist = []
            dict = {'line': 1}
            if row.voteType in [const.voteWar, const.voteKickMember, const.voteCEO]:
                owner = cfg.eveowners.Get(row.parameter)
                dict['text'] = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfoEntry', ownerName=owner.ownerName)
                dict['itemID'] = row.parameter
                dict['typeID'] = owner.typeID
                scrolllist.append(listentry.Get('Text', dict))
            elif row.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                dict['text'] = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfoTypeNameAndLocation', typeID=row.parameter1, location=row.parameter2)
                dict['itemID'] = row.parameter
                dict['typeID'] = row.parameter1
                scrolllist.append(listentry.Get('Text', dict))
            return scrolllist
        except:
            log.LogException()
            sys.exc_clear()

    def ShowSanctionableActionsNotInEffect(self, showExpired = False, *args):
        try:
            try:
                sm.GetService('corpui').ShowLoad()
                if not sm.GetService('corp').CanViewVotes(eve.session.corpid):
                    self.SetHint(localization.GetByLabel('UI/Corporations/AccessRestrictions/MustBeCEODirectorOrShareholder'))
                    return
                if showExpired:
                    if not eve.Message('ConfirmShowAllSanctionableActions', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                        return
                    uix.HideButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/AccessRestrictions/ShowAll'))
                    state = 0
                else:
                    uix.ShowButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/AccessRestrictions/ShowAll'))
                    state = 2
                scrolllist = []
                self.sr.scroll.Clear()
                voteCases = {}
                for row in sm.GetService('corp').GetVoteCasesByCorporation(eve.session.corpid).itervalues():
                    voteCases[row.voteCaseID] = row

                rows = sm.GetService('corp').GetSanctionedActionsByCorporation(eve.session.corpid, state)
                owners = []
                for row in rows.itervalues():
                    if row.voteType in [const.voteCEO, const.voteWar, const.voteKickMember] and row.parameter:
                        if row.parameter not in owners:
                            owners.append(row.parameter)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for row in rows.itervalues():
                    if row.voteType in [const.voteItemUnlock,
                     const.voteCEO,
                     const.voteWar,
                     const.voteShares,
                     const.voteKickMember,
                     const.voteItemLockdown] and row.parameter == 0:
                        continue
                    voteType = self.voteTypes[row.voteType]
                    title = voteCases[row.voteCaseID].voteCaseText
                    description = voteCases[row.voteCaseID].description
                    expires = util.FmtDate(row.expires)
                    actedUpon = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.actedUpon]
                    inEffect = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.inEffect]
                    rescended = localization.GetByLabel('UI/Generic/No')
                    if row.timeRescended:
                        rescended = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=rescended, timestamp=util.FmtDate(row.timeRescended))
                    if row.timeActedUpon:
                        actedUpon = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=actedUpon, timestamp=util.FmtDate(row.timeActedUpon))
                    label = '<t>'.join((voteType,
                     title,
                     description,
                     expires,
                     actedUpon,
                     inEffect,
                     rescended))
                    data = {'GetSubContent': self.GetNotInEffectSanctionedActionSubContent,
                     'label': label,
                     'groupItems': None,
                     'id': ('corpsanie', row.voteCaseID),
                     'tabs': [],
                     'state': 'locked',
                     'row': row,
                     'voteCases': voteCases,
                     'showicon': 'hide',
                     'BlockOpenWindow': 1}
                    scrolllist.append(listentry.Get('Group', data))
                    uicore.registry.SetListGroupOpenState(('corpsanie', row.voteCaseID), 0)

                self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.headers, noContentHint=localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NoNotInEffect'))
            finally:
                sm.GetService('corpui').HideLoad()

        except:
            log.LogException()
            sys.exc_clear()

    def GetNotInEffectSanctionedActionSubContent(self, nodedata, *args):
        try:
            row = nodedata.row
            voteCases = nodedata.voteCases
            if row.voteType == const.voteGeneral:
                fields = {}
                voteCaseOptions = sm.GetService('corp').GetVoteCaseOptions(row.voteCaseID)
                fields['Decision'] = voteCaseOptions[row.optionID].optionText
                return self.AddSanctionableEntry([fields, None])
            scrolllist = []
            if const.voteCEO != row.voteType and sm.GetService('corp').UserIsActiveCEO():
                if row.expires > blue.os.GetWallclockTime():
                    if not row.actedUpon:
                        action = [localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ImplementAction'), (self.ImplementSanctionedAction, row.voteCaseID)]
                        scrolllist.append(listentry.Get('Button', {'label': action[0],
                         'caption': localization.GetByLabel('UI/Commands/Apply'),
                         'OnClick': action[1][0],
                         'args': (action[1][1],)}))
            dict = {'line': 1}
            if row.voteType in [const.voteWar, const.voteKickMember, const.voteCEO]:
                owner = cfg.eveowners.Get(row.parameter)
                label = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfo')
                dict['text'] = label + '<t>' + owner.ownerName
                dict['itemID'] = row.parameter
                dict['typeID'] = owner.typeID
                scrolllist.append(listentry.Get('Text', dict))
            elif row.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                locationText = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/LocatedAt', location=row.parameter2)
                moreInfo = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfo')
                dict['text'] = moreInfo + '<t>' + cfg.invtypes.Get(row.parameter1).typeName + '<t>' + locationText
                dict['itemID'] = row.parameter
                dict['typeID'] = row.parameter1
                scrolllist.append(listentry.Get('Text', dict))
            return scrolllist
        except:
            log.LogException()
            sys.exc_clear()

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ImplementSanctionedAction(self, voteCaseID, wnd, *args):
        if not sm.GetService('corp').UserIsActiveCEO():
            label = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MustBeCEOToSanction')
            eve.Message('CustomError', {'error': label})
            return
        try:
            sm.GetService('corpui').ShowLoad()
            sm.GetService('corp').UpdateSanctionedAction(voteCaseID, 1)
            self.ShowSanctionableActionsNotInEffect()
        finally:
            sm.GetService('corpui').HideLoad()

    def AddSanctionableEntry(self, _entry):
        fields = _entry[0]
        action = _entry[1]
        scrolllist = []
        extraText = ''
        theFields = {'Decision': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Decision'),
         'expires': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Expires'),
         'actedUpon': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ActedUpon'),
         'In Effect': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/InEffect'),
         'timeActedUpon': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/TimeActedUpon'),
         'timeRescended': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/TimeRescinded')}
        if len(fields) and fields.has_key('Description'):
            scrolllist.append(listentry.Get('Text', {'text': fields['Description']}))
        for key in fields.iterkeys():
            if not theFields.has_key(key):
                continue
            field = fields[key]
            title = theFields[key]
            scrolllist.append(listentry.Get('LabelText', {'label': title,
             'text': field}))

        if action is not None:
            caption = localization.GetByLabel('UI/Commands/Apply')
            scrolllist.append(listentry.Get('Button', {'label': action[0],
             'caption': caption,
             'OnClick': action[1][0],
             'args': (action[1][1],)}))
        scrolllist.append(listentry.Get('Divider'))
        return scrolllist