import sys
import blue
import uthread
import util
import xtriui
import uix
import form
import listentry
import log
import uicls
import uiconst

class CorpSanctionableActions(uicls.Container):
    __guid__ = 'form.CorpSanctionableActions'
    __nonpersistvars__ = []

    def init(self):
        self.sr.inited = 0



    def Load(self, args):
        self.voteTypes = {const.voteCEO: mls.UI_CORP_NEWCEO,
         const.voteWar: mls.UI_CORP_DECLARATIONOFWAR,
         const.voteShares: mls.UI_CORP_CREATIONOFSHARES,
         const.voteKickMember: mls.UI_CORP_EXPULSION,
         const.voteGeneral: mls.UI_CORP_GENERALVOTE,
         const.voteItemUnlock: mls.UI_CORP_UNLOCKBLUEPRINT,
         const.voteItemLockdown: mls.UI_CORP_LOCKBLUEPRINT}
        self.headers = [mls.UI_GENERIC_TYPE,
         mls.UI_GENERIC_TITLE,
         mls.UI_GENERIC_DESCRIPTION,
         mls.UI_GENERIC_EXPIRES,
         mls.UI_GENERIC_ACTEDUPON,
         mls.UI_CORP_INEFFECT,
         mls.UI_CORP_RESCINDED]
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            buttonOptions = [[mls.UI_CORP_CLOSEDVOTES_SHOWALL,
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
            self.sr.tabs.Startup([[mls.UI_CORP_INEFFECT,
              self,
              self,
              'ineffect'], [mls.UI_CORP_NOTINEFFECT,
              self,
              self,
              'notineffect']], 'corpsanctionableact')
        sm.GetService('corpui').LoadTop('ui_7_64_5', mls.UI_CORP_SANCTIONABLEACTIONS)
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
                uix.HideButtonFromGroup(self.sr.mainBtns, mls.UI_CORP_CLOSEDVOTES_SHOWALL)
                scrolllist = []
                self.sr.scroll.Clear()
                if not sm.GetService('corp').CanViewVotes(eve.session.corpid):
                    self.SetHint(mls.UI_CORP_ACCESSDENIED9)
                    return 
                voteCases = {}
                voteCasesByCorp = sm.GetService('corp').GetVoteCasesByCorporation(eve.session.corpid)
                if voteCasesByCorp is not None:
                    voteCasesByCorp = voteCasesByCorp.itervalues()
                if voteCasesByCorp and len(voteCasesByCorp):
                    for row in voteCasesByCorp:
                        voteCases[row.voteCaseID] = row

                rows = sm.GetService('corp').GetSanctionedActionsByCorporation(eve.session.corpid, 1)
                if rows is not None:
                    rows = rows.itervalues()
                if rows and len(rows):
                    owners = []
                    for row in rows:
                        if row.voteType in [const.voteCEO, const.voteWar, const.voteKickMember] and row.parameter:
                            if row.parameter not in owners:
                                owners.append(row.parameter)

                    if len(owners):
                        cfg.eveowners.Prime(owners)
                    for row in rows:
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
                        actedUpon = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][row.actedUpon]
                        inEffect = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][row.inEffect]
                        rescended = mls.UI_GENERIC_NO
                        if row.timeRescended:
                            rescended += ' (%s)' % util.FmtDate(row.timeRescended)
                        if row.timeActedUpon:
                            actedUpon += ' (%s)' % util.FmtDate(row.timeActedUpon)
                        label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (voteType,
                         title,
                         description,
                         expires,
                         actedUpon,
                         inEffect,
                         rescended)
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

                self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.headers, noContentHint=mls.UI_CORP_NOSANCTIONABLEACTIONSINEFFECT)

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
            else:
                scrolllist = []
                dict = {'line': 1}
                if row.voteType in [const.voteWar, const.voteKickMember, const.voteCEO]:
                    owner = cfg.eveowners.Get(row.parameter)
                    dict['text'] = '  %s<t>' % mls.UI_GENERIC_MOREINFO + owner.ownerName
                    dict['itemID'] = row.parameter
                    dict['typeID'] = owner.typeID
                    scrolllist.append(listentry.Get('Text', dict))
                elif row.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                    locationText = mls.UI_SHARED_LOCATEDATSOMEWHERE % {'location': cfg.evelocations.Get(row.parameter2).locationName}
                    dict['text'] = '  %s<t>%s<t>%s' % (mls.UI_GENERIC_MOREINFO, cfg.invtypes.Get(row.parameter1).typeName, locationText)
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
                    self.SetHint(mls.UI_CORP_ACCESSDENIED9)
                    return 
                if showExpired:
                    if not eve.Message('ConfirmShowAllSanctionableActions', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                        return 
                    uix.HideButtonFromGroup(self.sr.mainBtns, mls.UI_CORP_CLOSEDVOTES_SHOWALL)
                    state = 0
                else:
                    uix.ShowButtonFromGroup(self.sr.mainBtns, mls.UI_CORP_CLOSEDVOTES_SHOWALL)
                    state = 2
                scrolllist = []
                self.sr.scroll.Clear()
                voteCases = {}
                for row in sm.GetService('corp').GetVoteCasesByCorporation(eve.session.corpid).itervalues():
                    voteCases[row.voteCaseID] = row

                rows = sm.GetService('corp').GetSanctionedActionsByCorporation(eve.session.corpid, state).itervalues()
                owners = []
                for row in rows:
                    if row.voteType in [const.voteCEO, const.voteWar, const.voteKickMember] and row.parameter:
                        if row.parameter not in owners:
                            owners.append(row.parameter)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for row in rows:
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
                    actedUpon = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][row.actedUpon]
                    inEffect = [mls.UI_GENERIC_NO, mls.UI_GENERIC_YES][row.inEffect]
                    rescended = mls.UI_GENERIC_NO
                    if row.timeRescended:
                        rescended += ' (%s)' % util.FmtDate(row.timeRescended)
                    if row.timeActedUpon:
                        actedUpon += ' (%s)' % util.FmtDate(row.timeActedUpon)
                    label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (voteType,
                     title,
                     description,
                     expires,
                     actedUpon,
                     inEffect,
                     rescended)
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

                self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.headers, noContentHint=mls.UI_CORP_NOSANCTIONABLEACTIONSNOTINEFFECT)

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
            else:
                scrolllist = []
                if const.voteCEO != row.voteType and sm.GetService('corp').UserIsActiveCEO():
                    if row.expires > blue.os.GetTime():
                        if not row.actedUpon:
                            action = [mls.UI_CORP_IMPLEMENTACTION, (self.ImplementSanctionedAction, row.voteCaseID)]
                            scrolllist.append(listentry.Get('Button', {'label': '%s' % action[0],
                             'caption': mls.UI_CMD_APPLY,
                             'OnClick': action[1][0],
                             'args': (action[1][1],)}))
                dict = {'line': 1}
                if row.voteType in [const.voteWar, const.voteKickMember, const.voteCEO]:
                    owner = cfg.eveowners.Get(row.parameter)
                    dict['text'] = '  %s<t>' % mls.UI_GENERIC_MOREINFO + owner.ownerName
                    dict['itemID'] = row.parameter
                    dict['typeID'] = owner.typeID
                    scrolllist.append(listentry.Get('Text', dict))
                elif row.voteType in [const.voteItemLockdown, const.voteItemUnlock]:
                    locationText = mls.UI_SHARED_LOCATEDATSOMEWHERE % {'location': cfg.evelocations.Get(row.parameter2).locationName}
                    dict['text'] = '  %s<t>%s<t>%s' % (mls.UI_GENERIC_MOREINFO, cfg.invtypes.Get(row.parameter1).typeName, locationText)
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
            eve.Message('CustomError', {'error': mls.UI_CORP_HINT52})
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
        theFields = {'Decision': mls.UI_GENERIC_DECISION,
         'expires': mls.UI_GENERIC_EXPIRES,
         'actedUpon': mls.UI_GENERIC_ACTEDUPON,
         'In Effect': mls.UI_CORP_INEFFECT,
         'timeActedUpon': mls.UI_CORP_TIMEACTEDUPON,
         'timeRescended': mls.UI_CORP_TIMERESCINDED}
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
            scrolllist.append(listentry.Get('Button', {'label': '%s' % action[0],
             'caption': mls.UI_CMD_APPLY,
             'OnClick': action[1][0],
             'args': (action[1][1],)}))
        scrolllist.append(listentry.Get('Divider'))
        return scrolllist




