import blue
import uthread
import util
import xtriui
import uix
import form
import dbg
import log
import listentry
import uicls
import uiconst
import form

class CorpApplications(uicls.Container):
    __guid__ = 'form.CorpApplications'
    __nonpersistvars__ = []
    DEFAULT_APPLICATIONS_HEIGHT = 125

    def ApplyAttributes(self, attributes):
        super(form.CorpApplications, self).ApplyAttributes(attributes)
        self.sr.viewingStatus = 0
        self.corpApplicationsContainer = uicls.Container(parent=self, name='corpApplicationsContainer', align=uiconst.TOALL)
        self.corpApplicationsLabel = uicls.Label(parent=self.corpApplicationsContainer, name='corpApplicationsLabel', align=uiconst.TOTOP, uppercase=True)
        self.sr.corpScroll = uicls.Scroll(parent=self.corpApplicationsContainer, name='corpScroll')
        self.sr.corpScroll.multiSelect = 0
        self.sr.corpScroll.stretchLastHeader = True
        self.sr.corpScroll.rightAlignHeaderLabels = [mls.UI_GENERIC_DATE]
        self.sr.corpScroll.sr.ignoreTabTrimming = True
        self.sr.corpScroll.sr.fixedColumns = {mls.UI_GENERIC_NAME: 256}
        self.personalApplicationsContainer = uicls.Container(parent=self, name='personalApplicationsContainer', align=uiconst.TOBOTTOM, padTop=const.defaultPadding, idx=0)
        personalApplicationsLabel = uicls.Label(parent=self.personalApplicationsContainer, name='personalApplicationsLabel', align=uiconst.TOTOP, text=mls.UI_CORP_MYAPPLICATIONS, uppercase=True)
        self.sr.personalScroll = uicls.Scroll(parent=self.personalApplicationsContainer, name='personalApplications')
        self.sr.personalScroll.multiSelect = 0
        self.sr.personalScroll.stretchLastHeader = True
        self.sr.personalScroll.rightAlignHeaderLabels = [mls.UI_GENERIC_DATE]
        self.sr.personalScroll.sr.ignoreTabTrimming = True
        self.sr.personalScroll.sr.fixedColumns = {mls.UI_GENERIC_NAME: 256}
        self.personalApplicationsContainer.height = self.DEFAULT_APPLICATIONS_HEIGHT



    def WithdrawApplications(self, *args):
        selected = self.sr.personalScroll.GetSelected()
        if not len(selected):
            return 
        for entry in selected:
            application = entry.application
            if eve.session.charid != application.characterID or eve.session.corpid != application.corporationID:
                self.WithdrawApplication(application.characterID, application.corporationID)




    def ShowCorporateApplications(self):
        log.LogInfo('ShowCorporateApplications')
        self.corpApplicationsLabel.SetText(mls.UI_CORP_APPLICATIONS_TO + ' ' + cfg.eveowners.Get(session.corpid).ownerName)
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            hint = mls.UI_CORP_HINT3
            if const.corpRolePersonnelManager & eve.session.corprole != const.corpRolePersonnelManager:
                log.LogInfo('ShowCorporateApplications Invalid Callee')
                hint = mls.UI_CORP_HINT23
            elif self is None or self.destroyed:
                log.LogInfo('ShowCorporateApplications Destroyed or None')
                hint = "You didn't see me."
            else:
                log.LogInfo('ShowCorporateApplications status', self.sr.viewingStatus)
                applications = sm.GetService('corp').GetApplicationsWithStatus(self.sr.viewingStatus)
                log.LogInfo('ShowCorporateApplications len(applications):', len(applications))
                owners = []
                for application in applications:
                    if application.characterID not in owners:
                        owners.append(application.characterID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for application in applications:
                    self._CorpApplications__AddApplicationToList(application, scrolllist, isMine=False)

            self.sr.corpScroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_NAME, mls.UI_GENERIC_DATE])
            if scrolllist:
                self.sr.corpScroll.ShowHint(None)
            else:
                self.sr.corpScroll.ShowHint(hint)

        finally:
            sm.GetService('corpui').HideLoad()




    def ShowMyApplications(self):
        log.LogInfo('ShowMyApplications')
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            hint = mls.UI_CORP_HINT3
            if self is None or self.destroyed:
                log.LogInfo('ShowMyApplications Destroyed or None')
            else:
                log.LogInfo('ShowMyApplications status', self.sr.viewingStatus)
                applications = sm.GetService('corp').GetMyApplicationsWithStatus(self.sr.viewingStatus)
                log.LogInfo('ShowMyApplications len(applications):', len(applications))
                owners = []
                for application in applications:
                    if application.corporationID not in owners:
                        owners.append(application.corporationID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for application in applications:
                    self._CorpApplications__AddApplicationToList(application, scrolllist, isMine=True)

            if scrolllist:
                self.sr.personalScroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_NAME, mls.UI_GENERIC_DATE])
                self.sr.personalScroll.ShowHint(None)
            else:
                self.sr.personalScroll.Load(fixedEntryHeight=19, contentList=scrolllist)
                self.sr.personalScroll.ShowHint(hint)

        finally:
            sm.GetService('corpui').HideLoad()




    def __AddApplicationToList(self, application, scrolllist, isMine = True):
        if application.status != self.sr.viewingStatus:
            return 
        status = ''
        if application.status == const.crpApplicationAppliedByCharacter:
            status = mls.UI_CORP_UNPROCESSED
        data = util.KeyVal()
        data.statusLabel = status
        data.isMine = isMine
        data.GetMenu = self.GetApplicationMenu
        data.corporation = sm.GetService('corp').GetCorporation(application.corporationID)
        data.application = application
        if isMine:
            dblClickFunc = lambda *args: self.ViewApplication(application.corporationID)
            id = application.corporationID
        else:
            dblClickFunc = lambda *args: self.CorpViewApplication(application.characterID, application.applicationText)
            id = application.characterID
        scrolllist.append(listentry.Get('User', {'charID': id,
         'applicationDate': application.applicationDateTime,
         'OnDblClick': dblClickFunc}))



    def GetApplicationMenu(self, entry):
        isMine = entry.sr.node.isMine
        application = entry.sr.node.application
        corporation = entry.sr.node.corporation
        status = entry.sr.node.statusLabel
        menu = []
        if isMine:
            withdraw = None
            menu.append((mls.UI_CMD_VIEWAPPLICATION, self.ViewApplication, (application.corporationID,)))
            if not (eve.session.charid == application.characterID and eve.session.corpid == application.corporationID):
                menu.append((mls.UI_CMD_WITHDRAW, self.WithdrawApplication, (application.characterID, corporation.corporationID)))
        else:
            menu.extend([(mls.UI_CMD_VIEWAPPLICATION, self.CorpViewApplication, (application.characterID, application.applicationText)), (mls.UI_CMD_ACCEPT, self.AcceptOrRejectApplication, (application.characterID, '', const.crpApplicationAcceptedByCorporation)), (mls.UI_CMD_REJECT, self.AcceptOrRejectApplication, (application.characterID, '', const.crpApplicationRejectedByCorporation))])
            menu.append(None)
            menu.append((mls.UI_CMD_SHOWINFO, self.ShowInfo, (cfg.eveowners.Get(application.characterID).typeID, application.characterID)))
            menu.extend(sm.GetService('menu').CharacterMenu(application.characterID))
        return menu



    def ShowInfo(self, typeID, itemID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)



    def OnCorporationApplicationChanged(self, applicantID, corporationID, change):
        log.LogInfo('OnCorporationApplicationChanged applicantID', applicantID, 'corporationID', corporationID, 'change', change)
        if self is None or self.destroyed:
            log.LogInfo('OnCorporationApplicationChanged self is None or self.destroyed')
            return 
        bAdd = 1
        bRemove = 1
        for (old, new,) in change.itervalues():
            if old is None and new is None:
                continue
            if old is not None:
                bAdd = 0
            if new is not None:
                bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('applications::OnCorporationApplicationChanged WTF')
        application = None
        if not bRemove:
            if eve.session.charid == applicantID:
                application = sm.GetService('corp').GetMyApplications(corporationID, forceUpdate=True)
            else:
                application = sm.GetService('corp').GetApplications(applicantID, forceUpdate=True)
            if application is not None:
                status = application.status
        if 'status' in change:
            if self.sr.viewingStatus in change['status']:
                (oldStatus, newStatus,) = change['status']
                if newStatus != self.sr.viewingStatus:
                    bRemove = True
                if newStatus == self.sr.viewingStatus:
                    bAdd = True
                if bRemove or bAdd:
                    self.ShowCorporateApplications()
                    self.ShowMyApplications()



    def WithdrawApplication(self, charid, corpid, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            sm.GetService('corp').DeleteApplication(corpid, charid)

        finally:
            sm.GetService('corpui').HideLoad()




    def ViewApplication(self, corporationID, application = None):
        if application is None:
            application = sm.GetService('corp').GetMyApplications(corporationID)
        if application is None:
            return 
        format = []
        status = mls.UI_CORP_HINT24
        format.append({'type': 'text',
         'text': mls.UI_CORP_YOURAPPLICATIONTOJOIN % {'corp': cfg.eveowners.Get(application.corporationID).name}})
        format.append({'type': 'push'})
        format.append({'type': 'bbline'})
        format.append({'type': 'labeltext',
         'label': mls.UI_GENERIC_STATUS,
         'text': status,
         'frame': 1})
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        if application.applicationText is not None and len(application.applicationText):
            format.append({'type': 'text',
             'text': application.applicationText,
             'frame': 1})
        else:
            format.append({'type': 'text',
             'text': ' ',
             'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        btn = uiconst.OK
        left = uicore.desktop.width / 2 - 400 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        retval = uix.HybridWnd(format, mls.UI_CORP_VIEWAPPLICATIONDETAILS, 1, None, btn, [left, top], 400, icon='ui_7_64_6')



    def CheckApplication(self, retval):
        if retval.has_key('appltext'):
            applicationText = retval['appltext']
            if len(applicationText) > 1000:
                return mls.UI_CORP_HINT4 % {'len': str(len(applicationText))}
        return ''



    def AcceptOrRejectApplication(self, characterID, applicationText, status):
        sm.GetService('corp').UpdateApplicationOffer(characterID, applicationText, status)



    def CorpViewApplication(self, characterID, applicationText = ''):
        corporationID = eve.session.corpid
        if const.corpRolePersonnelManager & eve.session.corprole != const.corpRolePersonnelManager:
            return 
        stati = {}
        format = []
        stati[const.crpApplicationRejectedByCorporation] = (mls.UI_CMD_REJECT, 1)
        stati[const.crpApplicationAcceptedByCorporation] = (mls.UI_CMD_ACCEPT, 0)
        format.append({'type': 'push'})
        format.append({'type': 'text',
         'text': '%s: <b>%s</b><br>' % (mls.UI_GENERIC_FROM, cfg.eveowners.Get(characterID).name)})
        format.append({'type': 'push'})
        format.append({'type': 'bbline'})
        i = 1
        for key in stati:
            if i == 1:
                lbl = mls.UI_GENERIC_STATUS
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
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'setvalue': applicationText,
         'key': 'appltext',
         'label': mls.UI_GENERIC_MESSAGE,
         'required': 0,
         'frame': 1,
         'readonly': 1})
        format.append({'type': 'errorcheck',
         'errorcheck': self.CheckApplication})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'bbline'})
        btn = uiconst.OKCANCEL
        left = uicore.desktop.width / 2 - 400 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        retval = uix.HybridWnd(format, mls.UI_CORP_VIEWAPPLICATIONDETAILS, 1, None, btn, [left, top], 400)
        if retval is not None:
            applicationText = retval['appltext']
            status = retval['stati']
            sm.GetService('corp').UpdateApplicationOffer(characterID, applicationText, status)




