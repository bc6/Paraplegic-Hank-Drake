import blue
import uthread
import util
import xtriui
import uix
import uicls
import uiconst
import form
import string
import listentry
import time
import uicls
import uiconst
import log
import localization

class FormAlliancesApplications(uicls.Container):
    __guid__ = 'form.AlliancesApplications'
    __nonpersistvars__ = []

    def CreateWindow(self):
        self.sr.inited = 1
        self.sr.rejectedContainer = uicls.Container(name='rejectedContainer', align=uiconst.TOTOP, parent=self, pos=(0, 0, 0, 18))
        showRejectedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ShowRejected')
        self.sr.viewRejected = uicls.Checkbox(text=showRejectedLabel, parent=self.sr.rejectedContainer, configName='viewRejected', retval=1, checked=0, groupname=None, callback=self.CheckBoxChecked, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         const.defaultPadding,
         150,
         0))
        self.sr.scroll = uicls.Scroll(name='applications', parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
        allianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliance')
        myApplicationsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/MyApplications')
        self.sr.tabs.Startup([[allianceLabel,
          self,
          self,
          'alliance'], [myApplicationsLabel,
          self,
          self,
          'myApplications']], 'allianceApplications')



    def Load(self, args):
        self.SetHint()
        if args == 'alliance':
            self.ShowAllianceApplications(self.sr.viewRejected.checked)
        elif args == 'myApplications':
            self.ShowMyApplications()



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def ShowAllianceApplications(self, viewRejected):
        log.LogInfo('ShowAllianceApplications')
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            headers = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/NoApplicationsFound')
            if eve.session.allianceid is None:
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/CorporationNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            elif const.corpRoleDirector & eve.session.corprole != const.corpRoleDirector:
                log.LogInfo('ShowAllianceApplications Invalid Callee')
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/RequireDirectorHint')
            elif self is None or self.destroyed:
                log.LogInfo('ShowAllianceApplications Destroyed or None')
            else:
                nameLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Name')
                statusLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status')
                headers = [nameLabel, statusLabel]
                applications = sm.GetService('alliance').GetApplications(viewRejected)
                log.LogInfo('ShowAllianceApplications len(applications):', len(applications))
                owners = []
                for application in applications.itervalues():
                    if application.corporationID not in owners:
                        owners.append(application.corporationID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for application in applications.itervalues():
                    self._FormAlliancesApplications__AddApplicationToList(application, scrolllist, 0)

            self.sr.rejectedContainer.state = uiconst.UI_PICKCHILDREN
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=headers, noContentHint=hint)

        finally:
            sm.GetService('corpui').HideLoad()




    def CheckBoxChecked(self, checkbox):
        self.ShowAllianceApplications(checkbox.checked)



    def ShowMyApplications(self):
        log.LogInfo('ShowMyApplications')
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            headers = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/NoApplicationsFound')
            if const.corpRoleDirector & eve.session.corprole != const.corpRoleDirector:
                log.LogInfo('ShowAllianceApplications Invalid Callee')
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/RequireDirectorHint')
            elif self is None or self.destroyed:
                log.LogInfo('ShowMyApplications Destroyed or None')
            else:
                nameLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Name')
                statusLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status')
                headers = [nameLabel, statusLabel]
                applications = sm.GetService('corp').GetAllianceApplications()
                log.LogInfo('ShowMyApplications len(applications):', len(applications))
                owners = []
                for application in applications.itervalues():
                    if application.allianceID not in owners:
                        owners.append(application.allianceID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for application in applications.itervalues():
                    self._FormAlliancesApplications__AddApplicationToList(application, scrolllist, 1)

            self.sr.rejectedContainer.state = uiconst.UI_HIDDEN
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=headers, noContentHint=hint)

        finally:
            sm.GetService('corpui').HideLoad()




    def __GetStatusStr(self, status):
        string = ''
        if status == const.allianceApplicationNew:
            string = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/New')
        elif status == const.allianceApplicationAccepted:
            string = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Accepted')
        elif status == const.allianceApplicationEffective:
            string = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Effective')
        elif status == const.allianceApplicationRejected:
            string = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Rejected')
        return string



    def __AddApplicationToList(self, application, scrolllist, myApplications):
        data = util.KeyVal()
        status = self._FormAlliancesApplications__GetStatusStr(application.state)
        if myApplications:
            data.label = '%s<t>%s' % (cfg.eveowners.Get(application.allianceID).ownerName, status)
            data.OnDblClick = self._ViewApplication
            data.GetMenu = self.GetApplicationMenu
        else:
            data.label = '%s<t>%s' % (cfg.eveowners.Get(application.corporationID).ownerName, status)
            data.OnDblClick = self.AllianceViewApplication
            data.GetMenu = self.GetAllianceMenu
        data.application = application
        scrolllist.append(listentry.Get('Generic', data=data))



    def GetAllianceMenu(self, entry):
        viewLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/View')
        return [(viewLabel, self.AllianceViewApplication, (entry,))]



    def GetApplicationMenu(self, entry):
        application = entry.sr.node.application
        viewLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/View')
        data = [(viewLabel, self._ViewApplication, (entry,))]
        if application.state == const.allianceApplicationRejected:
            deleteLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Delete')
            data.append((deleteLabel, self.DeleteApplication, (application,)))
        return data



    def GetEntry(self, allianceID, corporationID):
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.application.allianceID == allianceID and entry.application.corporationID == corporationID:
                return entry




    def OnAllianceApplicationChanged(self, allianceID, corporationID, change):
        log.LogInfo('OnAllianceApplicationChanged allianceID', allianceID, 'corporationID', corporationID, 'change', change)
        if self.sr.scroll is None:
            log.LogInfo('OnAllianceApplicationChanged no scroll')
            return 
        bAdd = 1
        bRemove = 1
        for (old, new,) in change.itervalues():
            if old is not None:
                bAdd = 0
            if new is not None:
                bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('applications::OnAllianceApplicationChanged WTF')
        if bAdd:
            log.LogInfo('OnAllianceApplicationChanged adding application')
            application = None
            activeTab = self.sr.tabs.GetSelectedArgs()
            myApplications = 0
            if eve.session.corpid == corporationID:
                if activeTab != 'myApplications':
                    return 
                application = sm.GetService('corp').GetAllianceApplications()[allianceID]
                myApplications = 1
            elif activeTab != 'alliance':
                return 
            application = sm.GetService('alliance').GetApplications()[corporationID]
            self.SetHint()
            scrolllist = []
            self._FormAlliancesApplications__AddApplicationToList(application, scrolllist, myApplications)
            if len(self.sr.scroll.sr.headers) > 0:
                self.sr.scroll.AddEntries(-1, scrolllist)
            else:
                self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers)
        elif bRemove:
            log.LogInfo('OnAllianceApplicationChanged removing application')
            entry = self.GetEntry(allianceID, corporationID)
            if entry is not None:
                self.sr.scroll.RemoveEntries([entry])
            else:
                log.LogWarn('OnAllianceApplicationChanged application not found')
        else:
            log.LogInfo('OnAllianceApplicationChanged updating application')
            entry = self.GetEntry(allianceID, corporationID)
            if entry is None:
                log.LogWarn('OnAllianceApplicationChanged application not found')
            if entry is not None:
                if 'state' in change:
                    (oldStatus, newStatus,) = change['state']
                    activeTab = self.sr.tabs.GetSelectedArgs()
                    if activeTab == 'alliance' and not self.sr.viewRejected.checked and newStatus == const.allianceApplicationRejected:
                        self.sr.scroll.RemoveEntries([entry])
                        return 
                    status = self._FormAlliancesApplications__GetStatusStr(newStatus)
                    if corporationID == eve.session.corpid:
                        label = '%s<t>%s' % (cfg.eveowners.Get(allianceID).ownerName, status)
                    else:
                        label = '%s<t>%s' % (cfg.eveowners.Get(corporationID).ownerName, status)
                    entry.panel.sr.node.label = label
                    entry.panel.sr.label.text = label



    def DeleteApplication(self, application, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            sm.GetService('corp').DeleteAllianceApplication(application.allianceID)

        finally:
            sm.GetService('corpui').HideLoad()




    def _ViewApplication(self, entry, *args):
        self.ViewApplication(entry.sr.node.application.allianceID, entry.sr.node.application)



    def ViewApplication(self, allianceID, application = None):
        if application is None:
            application = sm.GetService('corp').GetAllianceApplications()[allianceID]
        if application is None:
            return 
        stati = {}
        canEditStatus = 0
        canAppendNote = 0
        status = ''
        format = []
        status = self._FormAlliancesApplications__GetStatusStr(application.state)
        format.append({'type': 'bbline'})
        statusLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status')
        format.append({'type': 'labeltext',
         'label': statusLabel,
         'text': status,
         'frame': 1})
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        if application.applicationText is not None and len(application.applicationText):
            format.append({'type': 'textedit',
             'readonly': 1,
             'setvalue': application.applicationText,
             'frame': 1,
             'height': 96,
             'maxLength': 1000})
        else:
            format.append({'type': 'textedit',
             'readonly': 1,
             'setvalue': ' ',
             'frame': 1,
             'height': 96,
             'maxLength': 1000})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        btn = uiconst.OK
        left = uicore.desktop.width / 2 - 400 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        viewApplicationDetails = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ViewApplicationDetails')
        if application.state in [const.allianceApplicationAccepted, const.allianceApplicationEffective]:
            return uix.HybridWnd(format, viewApplicationDetails, 0, None, btn, [left, top], 400, unresizeAble=1)
        uix.HybridWnd(format, viewApplicationDetails, 1, None, btn, [left, top], 400, unresizeAble=1)



    def CheckApplication(self, retval):
        if retval.has_key('appltext'):
            applicationText = retval['appltext']
            textLength = len(applicationText)
            if textLength > 1000:
                return localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ApplicationTooLong', textLength=textLength)
        return ''



    def AllianceViewApplication(self, entry, *args):
        corporationID = entry.sr.node.application.corporationID
        allianceID = eve.session.allianceid
        if const.corpRoleDirector & eve.session.corprole != const.corpRoleDirector:
            return 
        application = entry.sr.node.application
        canEditStatus = 0
        canAppendNote = 0
        stati = {}
        status = self._FormAlliancesApplications__GetStatusStr(application.state)
        format = []
        if application.state == const.allianceApplicationNew:
            canEditStatus = 1
            canAppendNote = 1
            rejectLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Reject')
            acceptLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Accept')
            stati[const.allianceApplicationRejected] = (rejectLabel, 0)
            stati[const.allianceApplicationAccepted] = (acceptLabel, 1)
        elif application.state == const.allianceApplicationAccepted:
            canEditStatus = 0
            canAppendNote = 0
        elif application.state == const.allianceApplicationEffective:
            canEditStatus = 0
            canAppendNote = 0
        elif application.state == const.allianceApplicationRejected:
            canEditStatus = 0
            canAppendNote = 0
        statusLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status')
        fromLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/From')
        termsAndConditionsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/TermsAndConditions')
        format.append({'type': 'header',
         'text': fromLabel,
         'frame': 1})
        format.append({'type': 'text',
         'text': cfg.eveowners.Get(application.corporationID).ownerName,
         'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'header',
         'text': statusLabel,
         'frame': 1})
        format.append({'type': 'text',
         'text': status,
         'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'header',
         'text': termsAndConditionsLabel,
         'frame': 1})
        if canEditStatus == 0:
            format.append({'type': 'labeltext',
             'label': statusLabel,
             'text': status,
             'frame': 1})
            format.append({'type': 'bbline'})
        else:
            i = 1
            for key in stati:
                if i == 1:
                    lbl = 'Status'
                else:
                    lbl = ''
                (text, selected,) = stati[key]
                format.append({'type': 'checkbox',
                 'setvalue': selected,
                 'key': key,
                 'label': lbl,
                 'text': text,
                 'frame': 1,
                 'group': 'stati'})
                i = 0

            format.append({'type': 'bbline'})
        if canAppendNote == 1:
            allianceApplicationTextLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/AllianceApplicationText')
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'textedit',
             'setvalue': application.applicationText + ' --- ',
             'key': 'appltext',
             'label': allianceApplicationTextLabel,
             'required': 0,
             'frame': 1,
             'height': 96,
             'maxLength': 1000})
            format.append({'type': 'errorcheck',
             'errorcheck': self.CheckApplication})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'bbline'})
        else:
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'textedit',
             'setvalue': application.applicationText,
             'readonly': 1,
             'frame': 1,
             'height': 96,
             'maxLength': 1000})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'bbline'})
        if canEditStatus == 1 and canAppendNote == 1:
            btn = uiconst.OKCANCEL
        else:
            btn = uiconst.OK
        viewApplicationDetailsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ViewApplicationDetails')
        left = uicore.desktop.width / 2 - 400 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        if application.state == const.allianceApplicationEffective:
            return uix.HybridWnd(format, viewApplicationDetailsLabel, 0, None, btn, [left, top], 400, unresizeAble=1)
        retval = uix.HybridWnd(format, viewApplicationDetailsLabel, 1, None, btn, [left, top], 400, unresizeAble=1)
        if retval is not None and canEditStatus == 1 and canAppendNote == 1:
            applicationText = retval['appltext']
            status = retval['stati']
            if status == const.allianceApplicationAccepted:
                wars = sm.GetService('war').GetWars(corporationID, 1)
                if len(wars):
                    warningLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Warning')
                    warsWillBeAdoptedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/WarsWillBeAdopted')
                    format = []
                    format.append({'type': 'header',
                     'text': warningLabel,
                     'frame': 1})
                    format.append({'type': 'text',
                     'text': warsWillBeAdoptedLabel,
                     'frame': 1})
                    format.append({'type': 'push'})
                    declaredIDs = []
                    againstIDs = []
                    for war in wars.itervalues():
                        if war.declaredByID != corporationID:
                            declaredIDs.append(war.declaredByID)
                        if war.againstID != corporationID:
                            againstIDs.append(war.againstID)

                    if len(declaredIDs):
                        declaredByLabel = (localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/DeclaredBy'),)
                        format.append({'type': 'header',
                         'text': declaredByLabel,
                         'frame': 1})
                        for ownerID in declaredIDs:
                            format.append({'type': 'text',
                             'text': cfg.eveowners.Get(ownerID).ownerName,
                             'frame': 0})

                    if len(againstIDs):
                        againstLabel = (localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Against'),)
                        format.append({'type': 'header',
                         'text': againstLabel,
                         'frame': 1})
                        for ownerID in againstIDs:
                            format.append({'type': 'text',
                             'text': cfg.eveowners.Get(ownerID).ownerName,
                             'frame': 0})

                    format.append({'type': 'push',
                     'frame': 1})
                    format.append({'type': 'bbline'})
                    confirmAcceptLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ConfirmAccept')
                    format.append({'type': 'text',
                     'text': confirmAcceptLabel,
                     'frame': 0})
                    adoptWarsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/AdoptWars')
                    retval = uix.HybridWnd(format, adoptWarsLabel, 1, None, uiconst.OKCANCEL, [left, top], 400, unresizeAble=1)
                    if retval is None:
                        return 
            sm.GetService('alliance').UpdateApplication(corporationID, applicationText, status)
            if status == const.allianceApplicationAccepted:
                raise UserError('AcceptedApplicationsTake24HoursToBecomeEffective')




