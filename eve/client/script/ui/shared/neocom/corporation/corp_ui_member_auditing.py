import blue
import uthread
import util
import xtriui
import uix
import form
import string
import listentry
import time
import uiconst
import uicls
import localization
import localizationUtil

class CorpAuditing(uicls.Container):
    __guid__ = 'form.CorpAuditing'
    __nonpersistvars__ = []
    auditorMessageID = 60180

    def init(self):
        self.sr.notext = None
        self.sr.fromDate = None
        self.sr.toDate = None
        self.sr.mostRecentItem = None
        self.sr.oldestItem = None
        self.sr.memberID = None



    def Load(self, args):
        sm.GetService('corpui').LoadTop('ui_7_64_8', localization.GetByLabel('UI/Corporations/BaseCorporationUI/Auditing'))
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            toppar = uicls.Container(name='options', parent=self, align=uiconst.TOTOP, height=20)
            icon = xtriui.BaseButton(parent=toppar, width=20, height=20, align=uiconst.BOTTOMRIGHT)
            icon.hint = localization.GetByLabel('UI/Commands/Refresh')
            icon.Click = self.OnReturn
            self.sr.fwdBtn = uicls.Button(parent=toppar, icon='ui_77_32_41', iconSize=20, align=uiconst.BOTTOMRIGHT, left=6, func=self.Browse, args=1, hint=localization.GetByLabel('UI/Browser/Forward'))
            self.sr.backBtn = uicls.Button(parent=toppar, icon='ui_77_32_42', iconSize=20, align=uiconst.BOTTOMRIGHT, left=32, func=self.Browse, args=-1, hint=localization.GetByLabel('UI/Browser/Back'))
            nowSecs = blue.os.GetWallclockTime()
            (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(nowSecs + DAY)
            now = [year, month, day]
            (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(nowSecs - WEEK + DAY)
            lastWeek = [year, month, day]
            fromDate = uix.GetDatePicker(toppar, setval=lastWeek, left=5, top=14, idx=None)
            self.sr.fromDate = fromDate
            toDate = uix.GetDatePicker(toppar, setval=now, left=fromDate.left + fromDate.width + 4, top=14, idx=None)
            self.sr.toDate = toDate
            toppar.height = toDate.top + toDate.height
            memberIDs = sm.GetService('corp').GetMemberIDs()
            if len(memberIDs) < 24:
                memberlist = []
                cfg.eveowners.Prime(memberIDs)
                for charID in memberIDs:
                    memberlist.append([cfg.eveowners.Get(charID).name, charID])

                combo = uicls.Combo(label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/HaveToFindMember'), parent=toppar, options=memberlist, name='memberID', select=settings.user.ui.Get('memberID', None), callback=self.OnComboChange, width=100, pos=(toDate.left + toDate.width + 4,
                 toDate.top,
                 0,
                 0))
                self.sr.Set('Member', combo)
            else:
                searchMember = uicls.SinglelineEdit(name='searchMember', parent=toppar, align=uiconst.TOPLEFT, left=toDate.left + toDate.width + 6, top=toDate.top, width=92, maxLength=37, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/SearcForMember'))
                searchMember.OnReturn = self.SearchMember
                self.sr.searchMember = searchMember
            self.sr.scroll = uicls.Scroll(name='auditing', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.ShowJournal()



    def Browse(self, backforth, *args):
        self.ShowJournal(backforth)



    def OnComboChange(self, entry, header, value, *args):
        uthread.new(self.ShowJournal)



    def OnReturn(self, *args):
        uthread.new(self.ShowJournal)



    def SearchMember(self, *args):
        uthread.new(self.ShowJournal)



    def ParseDatePart(self, dateString):
        _CorpAuditing__dateseptbl = string.maketrans('/-. ', '----')
        date = string.translate(dateString, _CorpAuditing__dateseptbl)
        dp = date.split('-', 2)
        month = {1: localization.GetByLabel('UI/Common/Months/January'),
         2: localization.GetByLabel('UI/Common/Months/February'),
         3: localization.GetByLabel('UI/Common/Months/March'),
         4: localization.GetByLabel('UI/Common/Months/April'),
         5: localization.GetByLabel('UI/Common/Months/May'),
         6: localization.GetByLabel('UI/Common/Months/June'),
         7: localization.GetByLabel('UI/Common/Months/July'),
         8: localization.GetByLabel('UI/Common/Months/August'),
         9: localization.GetByLabel('UI/Common/Months/September'),
         10: localization.GetByLabel('UI/Common/Months/October'),
         11: localization.GetByLabel('UI/Common/Months/November'),
         12: localization.GetByLabel('UI/Common/Months/December')}
        return '%s %s, %s' % (month[int(dp[1])], int(dp[2]), int(dp[0]))



    def ParseDate(self, dateString):
        date = None
        if not dateString or len(str(dateString)) == 0:
            return 
        if ' ' in dateString:
            (d, t,) = dateString.split(' ')
            date = self.ParseDatePart(d)
            date += ' ' + t
        else:
            date = self.ParseDatePart(dateString)
        return "'%s'" % date



    def ShowJournal(self, browse = None):
        if self.sr.notext:
            self.sr.scroll.ShowHint(None)
        if eve.session.corprole & const.corpRoleAuditor != const.corpRoleAuditor:
            self.sr.notext = 1
            self.sr.scroll.Load(contentList=[])
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/AuditorRoleRequired', auditorMessageID=self.auditorMessageID))
            return 
        memberID = None
        memberIDs = sm.GetService('corp').GetMemberIDs()
        if len(memberIDs) < 24:
            memberID = self.sr.Member.GetValue()
        else:
            string = self.sr.searchMember.GetValue()
            if not string:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/HaveToFindMember')})
                uicore.registry.SetFocus(self.sr.searchMember)
                return 
            memberID = uix.Search(string.lower(), const.groupCharacter, filterCorpID=eve.session.corpid, searchWndName='corpMemberAuditingJournalSearch')
            if memberID:
                self.sr.searchMember.SetValue(cfg.eveowners.Get(memberID).name)
        if memberID is None:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/HaveToFindMember')})
            return 
        sm.GetService('loading').Cycle('Loading')
        fromDate = self.sr.fromDate.GetValue()
        toDate = self.sr.toDate.GetValue()
        if fromDate == toDate:
            toDate = toDate + DAY
        if browse is not None:
            interval = toDate - fromDate
            if browse == 1:
                toDate = toDate + interval
                fromDate = fromDate + interval
            else:
                toDate = toDate - interval
            fromDate = fromDate - interval
        (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(fromDate)
        self.sr.fromDate.ycombo.SetValue(year)
        self.sr.fromDate.mcombo.SetValue(month)
        self.sr.fromDate.dcombo.SetValue(day)
        (year, month, wd, day, hour, min, sec, ms,) = util.GetTimeParts(toDate)
        self.sr.toDate.ycombo.SetValue(year)
        self.sr.toDate.mcombo.SetValue(month)
        self.sr.toDate.dcombo.SetValue(day)
        scrolllist = []
        rowsPerPage = 10
        (logItemEventRows, crpRoleHistroyRows,) = sm.RemoteSvc('corpmgr').AuditMember(memberID, fromDate, toDate, rowsPerPage)
        logItems = []
        for row in logItemEventRows:
            logItems.append(row)

        roleItems = []
        for row in crpRoleHistroyRows:
            roleItems.append(row)

        logItems.sort(lambda x, y: cmp(y.eventDateTime, x.eventDateTime))
        roleItems.sort(lambda x, y: cmp(y.changeTime, x.changeTime))
        roleRows = sm.GetService('corp').GetRoles()
        roles = {}
        for role in roleRows:
            roles[role.roleID] = role.shortDescription

        self.sr.mostRecentItem = None
        self.sr.oldestItem = None
        ix = 0
        if 0 == len(logItems) and 0 == len(roleItems):
            self.sr.mostRecentItem = toDate
            self.sr.oldestItem = fromDate
        while len(logItems) or len(roleItems):
            ix += 1
            if ix > rowsPerPage:
                break
            logItem = None
            roleItem = None
            if len(logItems):
                logItem = logItems[0]
            if len(roleItems):
                roleItem = roleItems[0]
            if logItem is not None and roleItem is not None:
                if logItem.eventDateTime > roleItem.changeTime:
                    roleItem = None
                else:
                    logItem = None
            time = ''
            action = ''
            if logItem is not None:
                del logItems[0]
                time = util.FmtDate(logItem.eventDateTime, 'ss')
                if self.sr.mostRecentItem is None:
                    self.sr.mostRecentItem = logItem.eventDateTime
                if self.sr.oldestItem is None:
                    self.sr.oldestItem = logItem.eventDateTime
                if self.sr.oldestItem > logItem.eventDateTime:
                    self.sr.oldestItem = logItem.eventDateTime
                if self.sr.mostRecentItem < logItem.eventDateTime:
                    self.sr.mostRecentItem = logItem.eventDateTime
                corpName = cfg.eveowners.Get(logItem.corporationID).name if logItem.corporationID else ''
                if logItem.eventTypeID == 12:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/CreatedCorporation', corpName=corpName)
                elif logItem.eventTypeID == 13:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/DeletedCorporation', corpName=corpName)
                elif logItem.eventTypeID == 14:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/LeftCorporation', corpName=corpName)
                elif logItem.eventTypeID == 15:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/AppliedForMembershipOfCorporation', corpName=corpName)
                if logItem.eventTypeID == 16:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/BecameCEOOfCorporation', corpName=corpName)
                elif logItem.eventTypeID == 17:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/LeftCEOPositionOfCorporation', corpName=corpName)
                elif logItem.eventTypeID == 44:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/JoinedCorporation', corpName=corpName)
                action = `logItem`
            if roleItem is not None:
                del roleItems[0]
                time = util.FmtDate(roleItem.changeTime, 'ss')
                if self.sr.mostRecentItem is None:
                    self.sr.mostRecentItem = roleItem.changeTime
                if self.sr.oldestItem is None:
                    self.sr.oldestItem = roleItem.changeTime
                if self.sr.oldestItem > roleItem.changeTime:
                    self.sr.oldestItem = roleItem.changeTime
                if self.sr.mostRecentItem < roleItem.changeTime:
                    self.sr.mostRecentItem = roleItem.changeTime
                rolesBefore = []
                rolesAfter = []
                for roleID in roles.iterkeys():
                    if roleItem.oldRoles & roleID == roleID:
                        rolesBefore.append(roleID)
                    if roleItem.newRoles & roleID == roleID:
                        rolesAfter.append(roleID)

                added = []
                removed = []
                kept = []
                for roleID in roles.iterkeys():
                    if roleID in rolesBefore:
                        if roleID in rolesAfter:
                            kept.append(roleID)
                        else:
                            removed.append(roleID)
                    elif roleID in rolesAfter:
                        added.append(roleID)

                issuerID = roleItem.issuerID
                if issuerID == -1:
                    issuerID = const.ownerCONCORD
                actionOwner = cfg.eveowners.GetIfExists(issuerID)
                addedRoleNames = [ roles[roleID] for roleID in added ]
                removedRoleNames = [ roles[roleID] for roleID in removed ]
                keptRoleNames = [ roles[roleID] for roleID in kept ]
                cerberizedAddedRoleNames = localizationUtil.FormatGenericList(addedRoleNames)
                cerberizedRemovedRoleNames = localizationUtil.FormatGenericList(removedRoleNames)
                cerberizedKeptRoleNames = localizationUtil.FormatGenericList(keptRoleNames)
                rolesAddedLabel = ''
                rolesRemovedLabel = ''
                rolesKeptLabel = ''
                if len(addedRoleNames) > 0:
                    rolesAddedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/RolesAdded', listOfAddedRoles=cerberizedAddedRoleNames)
                if len(removedRoleNames) > 0:
                    rolesRemovedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/RolesRemoved', listOfRemovedRoles=cerberizedRemovedRoleNames)
                if len(keptRoleNames) > 0:
                    rolesKeptLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/RolesKept', listOfKeptRoles=cerberizedKeptRoleNames)
                summaryLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/SummaryOfChanges', firstListMessage=rolesAddedLabel, secondListMessage=rolesRemovedLabel, thirdListMessage=rolesKeptLabel)
                unknownIssuer = localization.GetByLabel('UI/Common/Unknown')
                corpName = cfg.eveowners.Get(roleItem.corporationID).name
                if actionOwner is None:
                    if roleItem.grantable:
                        action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/UnknownCharChangedGrantableRoles', charName=unknownIssuer, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
                    else:
                        action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/UnknownCharChangedRoles', charName=unknownIssuer, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
                elif roleItem.grantable:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/KnownCharChangedGrantableRoles', changingChar=issuerID, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
                action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/KnownCharChangedRoles', changingChar=issuerID, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
            text = '%s<t>%s' % (time, action)
            scrolllist.append(listentry.Get('Text', {'text': text,
             'line': 1,
             'canOpen': 'Action'}))

        if 0 == len(scrolllist):
            scrolllist.append(listentry.Get('Text', {'text': localization.GetByLabel('UI/Common/NoDataAvailable'),
             'line': 1}))
        self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Date'), localization.GetByLabel('UI/Common/Action')])
        if not len(scrolllist):
            self.sr.notext = 1
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/NoAuditingRecordsFound'))
        else:
            self.sr.notext = 0
        self.sr.fwdBtn.state = uiconst.UI_NORMAL
        self.sr.backBtn.state = uiconst.UI_NORMAL
        sm.GetService('loading').StopCycle()




