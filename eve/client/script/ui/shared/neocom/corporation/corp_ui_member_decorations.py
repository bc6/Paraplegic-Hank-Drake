import blue
import util
import uix
import form
import string
import listentry
import time
import uicls
import uiconst

class CorpDecorations(uicls.Container):
    __guid__ = 'form.CorpDecorations'
    __nonpersistvars__ = []

    def init(self):
        self.sr.notext = None
        self.sr.fromDate = None
        self.sr.toDate = None
        self.sr.mostRecentItem = None
        self.sr.oldestItem = None
        self.sr.memberID = None



    def Load(self, args):
        sm.GetService('corpui').LoadTop('50_16', mls.UI_GENERIC_DECORATIONS)
        if not self.sr.Get('inited', 0):
            if const.corpRolePersonnelManager & eve.session.corprole == const.corpRolePersonnelManager:
                btns = []
                btns.append([mls.UI_GENERIC_CREATEDECORATION,
                 self.CreateDecorationForm,
                 None,
                 None])
                self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
                buttons = uicls.ButtonGroup(btns=btns, parent=self.toolbarContainer)
                self.toolbarContainer.height = 20 if not len(btns) else buttons.height
            self.sr.scroll = uicls.Scroll(name='decorations', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.scroll.sr.id = 'corp_decorations_scroll'
            self.sr.inited = 1
        self.LoadDecorations()



    def CreateDecorationForm(self, *args):
        wnd = sm.GetService('window').GetWindow('MedalRibbonPickerWindow', create=1, maximize=1)



    def LoadDecorations(self, *args):
        scrolllist = []
        (medals, medalDetails,) = sm.GetService('medals').GetAllCorpMedals(session.corpid)
        for medal in medals:
            medalid = medal.medalID
            title = medal.title
            description = medal.description
            createdate = medal.date
            creator = cfg.eveowners.Get(medal.creatorID).name
            recipients = medal.noRecepients
            details = medalDetails.Filter('medalID')
            if details and details.has_key(medalid):
                details = details.get(medalid)
            label = '%s<t>%s<t>%s<t>%s<t>%s' % (title,
             creator,
             util.FmtDate(createdate, 'ss'),
             '',
             recipients)
            data = {'GetSubContent': self.GetDecorationSubContent,
             'label': label,
             'groupItems': None,
             'medal': medal,
             'details': details,
             'id': ('corpdecorations', medalid),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'hint': description,
             'sort_%s' % mls.UI_GENERIC_TITLE: title.lower(),
             'sort_%s' % mls.UI_GENERIC_DESCRIPTION: description.lower(),
             'sort_%s' % mls.UI_GENERIC_DATE: createdate}
            scrolllist.append(listentry.Get('Group', data))

        headers = [mls.UI_GENERIC_RECIPIENT,
         mls.UI_CONTRACTS_ISSUER,
         mls.UI_GENERIC_DATE,
         mls.UI_GENERIC_REASON,
         mls.UI_GENERIC_AWARDED]
        self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=mls.UI_GENERIC_NODECORATIONS)



    def GetDecorationSubContent(self, nodedata, *args):
        m = nodedata.medal
        d = nodedata.details
        medalid = m.medalID
        title = m.title
        description = m.description
        createdate = m.date
        scrolllist = []
        entry = sm.StartService('info').GetMedalEntry(None, m, d)
        if entry:
            scrolllist.append(entry)
        data = {'GetSubContent': self.GetMedalSubContent,
         'label': mls.UI_GENERIC_VIEWAWARDEES,
         'groupItems': None,
         'medal': m,
         'id': ('corpdecorationdetails', medalid),
         'tabs': [],
         'state': 'locked',
         'showicon': 'hide',
         'hint': description,
         'sublevel': 1,
         'sort_%s' % mls.UI_GENERIC_TITLE: title.lower(),
         'sort_%s' % mls.UI_GENERIC_DESCRIPTION: description.lower(),
         'sort_%s' % mls.UI_GENERIC_DATE: createdate}
        scrolllist.append(listentry.Get('Group', data))
        return scrolllist



    def GetMedalSubContent(self, nodedata, *args):
        m = nodedata.medal
        medalid = m.medalID
        recipients = sm.GetService('medals').GetRecipientsOfMedal(medalid)
        scrolllist = []
        recipientsunified = {}
        if recipients:
            for recipient in recipients:
                if not recipientsunified.has_key(recipient.recepientID):
                    recipientsunified[recipient.recepientID] = [recipient]
                else:
                    recipientsunified[recipient.recepientID].append(recipient)

        if recipientsunified:
            for (recipient, data,) in recipientsunified.iteritems():
                theyareallthesame = data[0]
                recipientID = recipient
                issuerID = theyareallthesame.issuerID
                date = theyareallthesame.date
                (statusID, statusName,) = self.GetStatus(theyareallthesame.status)
                reason = theyareallthesame.reason
                awarded = len(data)
                label = '%s<t>%s<t>%s<t>%s<t>%s' % (cfg.eveowners.Get(recipientID).name,
                 cfg.eveowners.Get(issuerID).name,
                 util.FmtDate(date, 'ss'),
                 reason,
                 awarded)
                data = {'label': label,
                 'sublevel': 2,
                 'id': m.medalID,
                 'line': 1,
                 'typeID': const.typeCharacterAmarr,
                 'itemID': recipientID,
                 'showinfo': 1,
                 'sort_%s' % mls.UI_GENERIC_TITLE: '_%s' % label.lower(),
                 'sort_%s' % mls.UI_GENERIC_STATUS: statusName}
                scrolllist.append(listentry.Get('Generic', data))

        return scrolllist



    def GetStatus(self, st):
        statuses = sm.GetService('medals').GetMedalStatuses()
        for status in statuses:
            if status.statusID == st:
                return status




    def OnCorporationMedalAdded(self, *args):
        if self and not self.destroyed:
            if self.sr.Get('inited', 0):
                self.LoadDecorations()




