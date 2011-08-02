import sys
import util
import uix
import uiutil
import form
import listentry
import log
import uicls
import uiconst

class CorpUIHome(uicls.Container):
    __guid__ = 'form.CorpUIHome'
    __nonpersistvars__ = []

    def OnClose_(self, *args):
        if self.sr.Get('offices', None) is not None:
            self.sr.offices.RemoveListener(self)



    def Load(self, args):
        self.canEditCorp = not util.IsNPC(eve.session.corpid) and const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector
        sm.GetService('corpui').LoadTop(None, None)
        if not self.sr.Get('inited', 0):
            self.OnInitializePanel()



    def OnInitializePanel(self):
        if not self or self.destroyed:
            return 
        self.sr.inited = 1
        if not self.sr.Get('offices'):
            self.sr.offices = None
        self.topContainer = uicls.Container(name='topContainer', align=uiconst.TOTOP, parent=self, height=54)
        self.mainContainer = uicls.Container(name='mainContainer', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self)
        self.logoContainer = uicls.Container(name='logoContainer', align=uiconst.TOLEFT, parent=self.topContainer, width=60)
        self.captionContainer = uicls.Container(name='captionContainer', align=uiconst.TOALL, pos=(10, 8, 10, 8), parent=self.topContainer)
        self.LoadLogo(eve.session.corpid)
        bulletinParent = uicls.Container(name='bulletinParent', parent=self.mainContainer, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        detailsParent = uicls.Container(name='detailsParent', parent=self.mainContainer, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        tabs = [[mls.UI_CORP_DETAILS,
          detailsParent,
          self,
          'details']]
        if not util.IsNPC(session.corpid):
            tabs.insert(0, [mls.UI_CORP_BULLETINS,
             bulletinParent,
             self,
             'bulletin'])
        self.sr.tabs = uicls.TabGroup(name='corphometabs', parent=self.mainContainer, idx=0)
        self.sr.tabs.Startup(tabs, 'corphometabs')
        btns = []
        if const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            btns.append(['corporationAddBulletinsBtn',
             mls.UI_CORP_ADDBULLETIN,
             self.AddBulletin,
             None,
             None])
            uicls.ButtonGroup(btns=btns, parent=bulletinParent, line=1, unisize=1, forcedButtonNames=True)
        if not util.IsNPC(session.corpid):
            uicls.Container(name='push', parent=bulletinParent, align=uiconst.TOLEFT, width=const.defaultPadding)
            self.messageArea = uicls.Edit(parent=bulletinParent, readonly=1, hideBackground=1)
            self.messageArea.AllowResizeUpdates(1)
            self.LoadBulletins()
        btns = []
        if getattr(self, 'canEditCorp', False):
            btns.append(['corporationEditDetailsBtn',
             mls.UI_CMD_EDITDETAILS,
             self.EditDetails,
             None,
             None])
        if sm.GetService('corp').UserIsCEO():
            btns.append(['corporationDividendsBtn',
             mls.UI_CMD_DIVIDENDS,
             self.PayoutDividendForm,
             None,
             None])
            btns.append(['corporationDivisionsBtn',
             mls.UI_CMD_DIVISIONS,
             self.DivisionsForm,
             None,
             None])
        else:
            btns.append(['corporationCreateNewCorpBtn',
             mls.UI_CMD_CREATENEWCORP,
             self.CreateCorpForm,
             None,
             None])
            if not util.IsNPC(eve.session.corpid):
                corpSvc = sm.StartService('corp')
                (canLeave, error, errorDetails,) = corpSvc.CanLeaveCurrentCorporation()
                if not canLeave and error == 'CrpCantQuitNotInStasis':
                    btns.append(['corporationRemoveRoles',
                     mls.UI_CMD_REMOVEALLROLES2,
                     self.RemoveAllRoles,
                     None,
                     None])
                else:
                    btns.append(['corporationResign',
                     mls.UI_CMD_QUITCORP2,
                     self.ResignFromCorp,
                     None,
                     None])
                if corpSvc.UserBlocksRoles():
                    btns.append(['corporationUnblockRoles',
                     mls.UI_CMD_ALLOWROLES,
                     self.AllowRoles,
                     None,
                     None])
        uicls.ButtonGroup(btns=btns, parent=detailsParent, line=0, unisize=1, forcedButtonNames=True)
        self.sr.scroll = uicls.Scroll(name='detailsScroll', parent=detailsParent, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.LoadScroll()



    def LoadBulletins(self):
        txt = sm.GetService('corp').GetFormattedBulletins()
        self.messageArea.LoadHTML(txt)



    def LoadLogo(self, corporationID):
        if self is None or self.destroyed:
            return 
        loc = getattr(self, 'logoContainer', None)
        if loc is not None:
            uix.Flush(loc)
            uiutil.GetLogoIcon(itemID=corporationID, parent=loc, align=uiconst.RELATIVE, name='logo', state=uiconst.UI_NORMAL, left=12, top=3, idx=0, size=48, ignoreSize=True)
        loc = getattr(self, 'captionContainer', None)
        if loc is not None:
            uix.Flush(loc)
            caption = uicls.CaptionLabel(text='%s' % cfg.eveowners.Get(eve.session.corpid).ownerName, parent=loc, align=uiconst.RELATIVE)
            caption.left = 0
            infoicon = uicls.InfoIcon(typeID=const.typeCorporation, itemID=corporationID, parent=loc, size=16, left=caption.width + 4, top=3, state=uiconst.UI_NORMAL)



    def EditDetails(self, *args):
        if not const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector:
            eve.Message('OnlyCEOOrEquivCanEditCorp')
            return None
        else:
            wnd = sm.GetService('window').GetWindow('editcorpdetails', 1, decoClass=form.EditCorpDetails)
            if wnd.ShowModal() == uiconst.ID_OK:
                return wnd.result
            return None



    def AddBulletin(self, *args):
        sm.GetService('corp').EditBulletin(None, isAlliance=False)



    def PayoutDividendForm(self, *args):
        if getattr(self, 'openingDividendForm', False):
            return 
        self.openingDividendForm = True
        try:
            if not sm.GetService('corp').UserIsCEO():
                eve.Message('OnlyCEOCanPayoutDividends')
                return 
            maxAmount = sm.RemoteSvc('account').GetCashBalance(1, 1000)
            if maxAmount < 1:
                eve.Message('CorpHasNoMoneyToPayoutDividends')
                return 
            payShareholders = 0
            format = [{'type': 'btline'},
             {'type': 'push',
              'frame': 1},
             {'type': 'text',
              'text': mls.UI_CORP_HINT37,
              'frame': 1},
             {'type': 'push',
              'frame': 1},
             {'type': 'btline'},
             {'type': 'push',
              'frame': 1}]
            payShareholders = 0
            payMembers = 1
            format.append({'type': 'text',
             'text': mls.UI_CORP_HINT38,
             'frame': 1})
            format.append({'type': 'checkbox',
             'required': 1,
             'group': 'OdividendType',
             'height': 16,
             'setvalue': 1,
             'key': payShareholders,
             'label': '',
             'text': mls.UI_CORP_SHAREHOLDERS,
             'frame': 1})
            format.append({'type': 'checkbox',
             'required': 1,
             'group': 'OdividendType',
             'height': 16,
             'setvalue': 0,
             'key': payMembers,
             'label': '',
             'text': mls.UI_CORP_MEMBERS,
             'frame': 1})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'btline'})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'text',
             'text': mls.UI_CORP_HINT39,
             'frame': 1})
            format.append({'type': 'text',
             'text': mls.UI_CORP_HINT40,
             'frame': 1})
            format.append({'type': 'edit',
             'key': 'payoutAmount',
             'setvalue': 1,
             'label': mls.UI_GENERIC_AMOUNT,
             'frame': 1,
             'floatonly': [1, maxAmount]})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'bbline'})
            retval = uix.HybridWnd(format, mls.UI_CORP_HINT41, 1, None, None, None, 340, 256, ignoreCurrent=0)
            if retval is not None:
                payShareholders = [1, 0][retval['OdividendType']]
                payoutAmount = retval['payoutAmount']
                sm.GetService('corp').PayoutDividend(payShareholders, payoutAmount)

        finally:
            self.openingDividendForm = False




    def DivisionsForm(self, *args):
        if not sm.GetService('corp').UserIsCEO():
            eve.Message('CrpAccessDenied', {'reason': mls.UI_CORP_HINT42})
            return 
        divisions = sm.GetService('corp').GetDivisionNames()
        format = [{'type': 'btline'},
         {'type': 'push',
          'frame': 1},
         {'type': 'text',
          'frame': 1,
          'text': mls.UI_CORP_HINT43},
         {'type': 'push',
          'frame': 1}]
        labelWidth = 160
        for i in xrange(1, 8):
            key = 'division%s' % i
            label = '%s (%s):' % (mls.UI_CORP_DIVISIONNAME, i)
            format.append({'type': 'edit',
             'setvalue': divisions[i],
             'label': label,
             'key': key,
             'frame': 1,
             'labelwidth': labelWidth,
             'maxlength': 50})

        format.append({'type': 'labeltext',
         'label': '%s (1):' % mls.UI_CORP_WALLETDIVISIONNAME,
         'text': mls.UI_CORP_MASTERWALLET,
         'frame': 1,
         'labelwidth': labelWidth})
        for i in xrange(9, 15):
            key = 'division%s' % i
            label = '%s (%s):' % (mls.UI_CORP_WALLETDIVISIONNAME, i - 7)
            format.append({'type': 'edit',
             'setvalue': divisions[i],
             'label': label,
             'key': key,
             'frame': 1,
             'labelwidth': labelWidth,
             'maxlength': 50})

        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        format.append({'type': 'errorcheck',
         'errorcheck': self.ApplyDivisionNames})
        wnd = uix.HybridWnd(format, mls.UI_CORP_DIVISIONNAMES, 0, minW=450, ignoreCurrent=0)
        if wnd:
            wnd.Maximize()



    def ApplyDivisionNames(self, retval):

        def KeyToInt(k):
            return int(k[len('division'):])


        new = dict([ (KeyToInt(k), v) for (k, v,) in retval.iteritems() ])
        current = sm.GetService('corp').GetDivisionNames()
        currentNamesForNewKeys = dict([ (k, current[k]) for k in new.iterkeys() ])
        if new != currentNamesForNewKeys:
            try:
                sm.GetService('corp').UpdateDivisionNames(*[ new.get(k, current[k]) for k in xrange(1, len(current) + 1) ])
            except UserError as e:
                msg = cfg.GetMessage(e.msg, e.dict)
                if msg.type == 'notify' and e.msg.find('CorpDiv') > -1:
                    sys.exc_clear()
                    return msg.text
                raise 
        return ''



    def CreateCorpForm(self, *args):
        wnd = sm.GetService('window').GetWindow('createcorp')
        if wnd is not None:
            wnd.Maximize()
        else:
            sm.GetService('sessionMgr').PerformSessionChange('corp.addcorp', self.ShowCreateCorpForm)



    def ShowCreateCorpForm(self, *args):
        if not eve.session.stationid:
            eve.Message('CanOnlyCreateCorpInStation')
            eve.session.ResetSessionChangeTimer('Failed criteria for creating a corporation')
            return 
        if sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
            eve.Message('CanNotCreateCorpAtPlayerOwnedStation')
            eve.session.ResetSessionChangeTimer('Failed criteria for creating a corporation')
            return 
        if not sm.GetService('corp').MemberCanCreateCorporation():
            cost = sm.GetService('corp').GetCostForCreatingACorporation()
            eve.Message('PlayerCantCreateCorporation', {'cost': cost})
            eve.session.ResetSessionChangeTimer('Failed criteria for creating a corporation')
            return 
        if sm.GetService('corp').UserIsCEO():
            eve.Message('CEOCannotCreateCorporation')
            eve.session.ResetSessionChangeTimer('Failed criteria for creating a corporation')
            return 
        wnd = sm.GetService('window').GetWindow('createcorporation', 1, decoClass=form.CreateCorp)



    def LoadScroll(self):
        if self is None or self.destroyed:
            return 
        if not self.sr.Get('scroll'):
            return 
        try:
            try:
                scrolllist = []
                sm.GetService('corpui').ShowLoad()
                self.ShowMyCorporationsDetails(scrolllist)
                self.ShowMyCorporationsOffices(scrolllist)
                self.ShowMyCorporationsStations(scrolllist)
                self.sr.scroll.Load(contentList=scrolllist)
            except:
                log.LogException()
                sys.exc_clear()

        finally:
            sm.GetService('corpui').HideLoad()




    def ShowMyCorporationsDetails(self, scrolllist):
        sm.GetService('corpui').ShowLoad()
        try:
            data = {'GetSubContent': self.GetSubContentDetails,
             'label': mls.UI_GENERIC_DETAILS,
             'groupItems': None,
             'id': ('corporation', 'details'),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))
            uicore.registry.SetListGroupOpenState(('corporation', 'details'), 1)

        finally:
            sm.GetService('corpui').HideLoad()




    def GetSubContentDetails(self, nodedata, *args):
        scrolllist = []
        corpinfo = sm.GetService('corp').GetCorporation()
        founderdone = 0
        if cfg.invtypes.Get(cfg.eveowners.Get(corpinfo.ceoID).typeID).groupID == const.groupCharacter:
            if corpinfo.creatorID == corpinfo.ceoID:
                ceoLabel = mls.UI_INFOWND_CEOANDFOUNDER
                founderdone = 1
            else:
                ceoLabel = mls.UI_GENERIC_CEO
            scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
             'label': ceoLabel,
             'text': cfg.eveowners.Get(corpinfo.ceoID).name,
             'typeID': const.typeCharacterAmarr,
             'itemID': corpinfo.ceoID}))
        if not founderdone and cfg.invtypes.Get(cfg.eveowners.Get(corpinfo.creatorID).typeID).groupID == const.groupCharacter:
            scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
             'label': mls.UI_INFOWND_FOUNDER,
             'text': cfg.eveowners.Get(corpinfo.creatorID).name,
             'typeID': const.typeCharacterAmarr,
             'itemID': corpinfo.creatorID}))
        if corpinfo.stationID:
            station = sm.RemoteSvc('stationSvc').GetStation(corpinfo.stationID)
            row = util.Row(['stationID', 'typeID'], [corpinfo.stationID, station.stationTypeID])
            jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(station.solarSystemID)
            locationName = cfg.evelocations.Get(station.stationID).locationName
            text = '%s - %s' % (locationName, uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})
            scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
             'label': mls.UI_CORP_HEADQUARTERS,
             'text': text,
             'typeID': station.stationTypeID,
             'itemID': corpinfo.stationID,
             'station': row,
             'GetMenu': lambda itemID = corpinfo.stationID, typeID = station.stationTypeID: sm.StartService('menu').CelestialMenu(itemID, typeID=typeID)}))
        for each in [('tickerName', mls.UI_GENERIC_TICKERNAME),
         ('shares', mls.UI_GENERIC_SHARES),
         ('memberCount', mls.UI_GENERIC_MEMBERCOUNT),
         ('taxRate', mls.UI_GENERIC_TAXRATE)]:
            if each[0] == 'memberCount' and util.IsNPC(eve.session.corpid):
                continue
            val = getattr(corpinfo, each[0], 0.0)
            if each[0] == 'taxRate':
                val = '%s %%' % (val * 100)
            scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
             'label': each[1],
             'text': val}))

        if corpinfo.url:
            scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
             'label': mls.UI_GENERIC_URL,
             'text': '<url=%s>%s</url>' % (corpinfo.url, corpinfo.url)}))
        scrolllist.append(listentry.Get('LabelTextTop', {'line': 1,
         'label': mls.UI_CORP_MEMBERSHIP_APPLICATIONS,
         'text': [mls.UI_SHARED_DISABLED, mls.UI_SHARED_ENABLED][corpinfo.isRecruiting]}))
        return scrolllist



    def ShowMyCorporationsOffices(self, scrolllist):
        sm.GetService('corpui').ShowLoad()
        try:
            data = {'GetSubContent': self.GetSubContentMyCorporationsOffices,
             'label': mls.UI_CORP_OFFICES,
             'groupItems': None,
             'id': ('corporation', 'offices'),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))
            uicore.registry.SetListGroupOpenState(('corporation', 'offices'), 0)

        finally:
            sm.GetService('corpui').HideLoad()




    def OnDataChanged(self, rowset, primaryKey, change, notificationParams):
        log.LogInfo('----------------------------------------------')
        log.LogInfo('OnDataChanged')
        log.LogInfo('primaryKey:', primaryKey)
        log.LogInfo('change:', change)
        log.LogInfo('notificationParams:', notificationParams)
        log.LogInfo('----------------------------------------------')
        if not (self and not self.destroyed):
            return 
        if self.sr.Get('offices', None) is not None:
            if rowset == self.sr.offices:
                self.LoadScroll()



    def GetSubContentMyCorporationsOffices(self, nodedata, *args):
        subcontent = []
        if self.sr.Get('offices', None) is None:
            self.sr.offices = sm.GetService('corp').GetMyCorporationsOffices()
            self.sr.offices.Fetch(0, len(self.sr.offices))
            self.sr.offices.AddListener(self)
        if self.sr.offices and len(self.sr.offices):
            for row in self.sr.offices:
                solarSystemID = sm.GetService('ui').GetStation(row.stationID).solarSystemID
                jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarSystemID)
                locationName = cfg.evelocations.Get(row.stationID).locationName
                label = '%s - %s' % (locationName, uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})
                subcontent.append((locationName.lower(), listentry.Get('Generic', {'label': label,
                  'station': row,
                  'GetMenu': self.GetMenu,
                  'typeID': row.typeID,
                  'itemID': row.stationID})))

        if not len(subcontent):
            subcontent.append(listentry.Get('Generic', {'label': mls.UI_CORP_HINT44}))
        else:
            subcontent = uiutil.SortListOfTuples(subcontent)
        return subcontent



    def GetMenu(self, entry):
        log.LogInfo('WQWQQWQW')
        station = entry.sr.node.station
        return sm.GetService('menu').CelestialMenu(station.stationID, typeID=station.typeID)



    def ShowMyCorporationsStations(self, scrolllist):
        sm.GetService('corpui').ShowLoad()
        try:
            data = {'GetSubContent': self.GetSubContentMyCorporationsStations,
             'label': mls.UI_GENERIC_STATIONS,
             'groupItems': None,
             'id': ('corporation', 'stations'),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))
            uicore.registry.SetListGroupOpenState(('corporation', 'stations'), 0)

        finally:
            sm.GetService('corpui').HideLoad()




    def GetSubContentMyCorporationsStations(self, nodedata, *args):
        subcontent = []
        rows = sm.GetService('corp').GetMyCorporationsStations()
        if rows and len(rows):
            for row in rows:
                solarSystemID = sm.GetService('ui').GetStation(row.stationID).solarSystemID
                jumps = sm.GetService('pathfinder').GetJumpCountFromCurrent(solarSystemID)
                locationName = cfg.evelocations.Get(row.stationID).locationName
                label = '%s - %s' % (locationName, uix.Plural(jumps, 'UI_SHARED_NUM_JUMP') % {'num': jumps})
                subcontent.append(listentry.Get('Generic', {'label': label,
                 'station': row,
                 'GetMenu': self.GetMenu,
                 'typeID': row.typeID,
                 'itemID': row.stationID}))

        if not len(subcontent):
            subcontent.append(listentry.Get('Generic', {'label': mls.UI_CORP_HINT45}))
        return subcontent



    def RemoveAllRoles(self, *args):
        corpSvc = sm.StartService('corp')
        (canLeave, error, errorDetails,) = corpSvc.CanLeaveCurrentCorporation()
        if not canLeave:
            if error == 'CrpCantQuitNotInStasis':
                if eve.Message('ConfirmRemoveAllRolesDetailed', errorDetails, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return 
                corpSvc.RemoveAllRoles(silent=True)
            else:
                raise UserError(error, errorDetails)



    def ResignFromCorp(self, *args):
        corpSvc = sm.StartService('corp')
        (canLeave, error, errorDetails,) = corpSvc.CanLeaveCurrentCorporation()
        if canLeave:
            corpSvc.KickOut(eve.session.charid)
        else:
            raise UserError(error, errorDetails)



    def AllowRoles(self, *args):
        if eve.Message('ConfirmAllowRoles', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        sm.StartService('corp').UpdateMember(eve.session.charid, None, None, None, None, None, None, None, None, None, None, None, None, None, 0)
        eve.Message('NotifyRolesAllowed', {})




class EditCorpBulletin(uicls.Window):
    __guid__ = 'form.EditCorpBulletin'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        isAlliance = attributes.isAlliance
        bulletin = attributes.bulletin
        self.scope = 'all'
        self.bulletin = bulletin
        self.bulletinID = None
        self.editDateTime = None
        self.isAlliance = isAlliance
        self.SetMinSize([420, 300])
        self.SetWndIcon('ui_7_64_6')
        self.SetCaption(mls.UI_CORP_EDITBULLETINCAPTION)
        self.SetTopparentHeight(45)
        main = uiutil.FindChild(self, 'main')
        main.left = main.top = main.width = main.height = const.defaultPadding
        uicls.Container(parent=self.sr.topParent, width=4, align=uiconst.TORIGHT, name='push')
        uicls.Container(parent=self.sr.topParent, width=120, align=uiconst.TOLEFT, name='push')
        titleInput = uicls.SinglelineEdit(name='titleInput', parent=self.sr.topParent, align=uiconst.TOBOTTOM, maxLength=100)
        titleInput.OnDropData = self.OnDropData
        self.sr.titleInput = titleInput
        l = uicls.Label(text=mls.UI_GENERIC_TITLE, parent=titleInput, width=64, height=12, left=48, top=4, fontsize=9, letterspace=2, state=uiconst.UI_DISABLED, uppercase=1)
        l.left = -l.textwidth - 6
        uicls.Container(parent=main, height=const.defaultPadding, align=uiconst.TOTOP, name='push')
        self.sr.messageEdit = uicls.EditPlainText(setvalue='', parent=main, maxLength=2000, showattributepanel=1)
        self.sr.bottom = uicls.Container(name='bottom', parent=self.sr.maincontainer, align=uiconst.TOBOTTOM, height=24, idx=0)
        uicls.ButtonGroup(btns=[[mls.UI_CMD_SUBMIT,
          self.ClickSend,
          None,
          None], [mls.UI_CMD_CANCEL,
          self.OnCancel,
          None,
          None]], parent=self.sr.bottom, line=False)
        if bulletin is not None:
            self.sr.titleInput.SetValue(bulletin.title)
            self.sr.messageEdit.SetValue(bulletin.body)
            self.bulletinID = bulletin.bulletinID
            self.editDateTime = bulletin.editDateTime



    def OnCancel(self, *args):
        self.SelfDestruct()



    def OnClose_(self, *args):
        self.messageEdit = None



    def IsAlliance(self):
        return self.isAlliance



    def ClickSend(self, *args):
        if getattr(self, 'sending', False):
            return 
        self.sending = True
        title = self.sr.titleInput.GetValue()
        body = self.sr.messageEdit.GetValue()
        if title == '' or body == '':
            self.sending = False
            raise UserError('CorpBulletinMustFillIn')
        if self.bulletinID is None:
            sm.GetService('corp').AddBulletin(title, body, self.isAlliance)
        else:
            sm.GetService('corp').UpdateBulletin(self.bulletinID, title, body, self.isAlliance, self.editDateTime)
        if not self or self.destroyed:
            return 
        self.SelfDestruct()




