import sys
import blue
import uthread
import uix
import uiutil
import xtriui
import form
import util
import listentry
import service
import dbutil
import uicls
import uiconst

class PetitionSvc(service.Service):
    __exportedcalls__ = {'Show': [service.ROLE_IGB]}
    __guid__ = 'svc.petition'
    __notifyevents__ = ['ProcessSessionChange',
     'OnNewPetition',
     'OnPetitionCreated',
     'OnClosePetition',
     'OnAssignPetition',
     'OnPetitionMessage']
    __servicename__ = 'petition'
    __displayname__ = 'Petition Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Starting Petitions')
        self.Reset()



    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.SelfDestruct()
        self.Reset()



    def ProcessSessionChange(self, isremote, session, change):
        if eve.session.charid is None:
            wnd = self.GetWnd()
            if wnd is not None and not wnd.destroyed:
                wnd.SelfDestruct()
                self.mine = None



    def OnNewPetition(self, petitionid):
        if eve.session.charid is None:
            return 
        uthread.pool('PetitionSvc::OnNewPetition', self._OnNewPetition, petitionid)



    def _OnNewPetition(self, petitionid):
        self.LogInfo('OnNewPetition')
        sm.GetService('neocom').Blink('help')
        self._ReloadVisible()



    def OnClosePetition(self, *args):
        if eve.session.charid is None:
            return 
        uthread.pool('PetitionSvc::OnClosePetition', self._OnClosePetition, *args)



    def _OnClosePetition(self, *args):
        self.LogInfo('OnClosePetition')
        sm.GetService('neocom').Blink('help')
        self._ReloadVisible()



    def OnAssignPetition(self, petitionID, assigneeid):
        if eve.session.charid is None:
            return 
        uthread.pool('PetitionSvc::OnAssignPetition', self._OnAssignPetition, petitionID, assigneeid)



    def _OnAssignPetition(self, petitionID, assigneeid):
        self.LogInfo('OnAssignPetition')
        self._ReloadVisible()



    def OnPetitionCreated(self, *args):
        if eve.session.charid is None:
            return 
        uthread.pool('PetitionSvc::OnPetitionCreated', self._OnPetitionCreated)



    def _OnPetitionCreated(self):
        self.LogInfo('OnPetitionCreated')
        self._ReloadVisible()



    def CheckNewMessages(self):
        newMessages = sm.RemoteSvc('petitioner').GetUnreadMessages()
        if len(newMessages) == 1:
            self.NewMessage(newMessages[0].petitionID, newMessages[0].text, newMessages[0].messageID)
        elif len(newMessages) > 1:
            if eve.Message('PetitionQuestion1', {'messages': len(newMessages)}, uiconst.YESNO) == uiconst.ID_YES:
                self.Show()



    def MarkAsRead(self, messageID):
        if messageID in self.read:
            return 
        self.read.append(messageID)
        sm.RemoteSvc('petitioner').MarkAsRead(messageID)



    def NewMessage(self, petitionID, message, messageID):
        self.MarkAsRead(messageID)
        eve.Message('PetPetitionResponse')
        sm.GetService('neocom').Blink('help')



    def Reset(self):
        self.wnd = None
        self.mine = None
        self.petitionee = None
        self.categories = None
        self.queues = None
        self.claimedpetitions = None
        self.loadingmessages = 0
        self.loadinglogs = 0
        self.read = []



    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()



    def Load(self, args):
        if not session.charid:
            return 
        if args in ('generic', 'rating'):
            viewwnd = self.GetViewWnd()
            if viewwnd is not None and viewwnd.sr.viewmessageform:
                viewwnd.sr.viewmessageform.state = uiconst.UI_HIDDEN
                if args == 'rating':
                    self.ShowRating()
        elif args == 'messages':
            self.LoadMessages()
        elif args == 'logs':
            self.LoadLogs()
        elif args == 'mypetitions':
            uthread.new(self.ShowMyPetitions)
        elif args == 'claimedpetitions':
            self.ShowClaimedPetitions()
        elif args in range(6):
            self.ShowPetitionQueue(args)
        self.SelectionChange([])



    def GetWnd(self, new = 0):
        wnd = sm.GetService('window').GetWindow('petitions')
        if not wnd and new:
            wnd = sm.GetService('window').GetWindow('petitions', 1)
            wnd.scope = 'station_inflight'
            wnd.sr.main = uiutil.GetChild(wnd, 'main')
            wnd.SetCaption(mls.UI_SHARED_PETITIONS)
            wnd.SetMinSize([400, 256])
            wnd.SetWndIcon('74_14')
            wnd.SetTopparentHeight(60)
            wnd.sr.scroll = uicls.Scroll(parent=wnd.sr.main, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            wnd.sr.scroll.sr.id = 'petitionScroll'
            wnd.sr.scroll.OnSelectionChange = self.SelectionChange
            wnd.sr.scroll.multiSelect = 0
            btns = [(mls.UI_CMD_VIEW,
              self.ShowPetitionClicked,
              (),
              84),
             (mls.UI_CMD_CLAIM,
              self.ClaimPetitionClicked,
              (),
              84),
             (mls.UI_CMD_DELETE,
              self.DeletePetitionClicked,
              (),
              84),
             (mls.UI_CMD_CANCEL,
              self.CancelPetitionClicked,
              (),
              84),
             (mls.UI_CMD_RATE,
              self.RatePetitionClicked,
              (),
              84)]
            wnd.sr.buttons = uicls.ButtonGroup(btns=btns, parent=wnd.sr.main, subalign=uiconst.CENTERLEFT, idx=0)
            uicls.ButtonGroup(btns=[[mls.UI_CMD_CREATENEWPETITION,
              self.NewPetition,
              None,
              None]], parent=wnd.sr.topParent, line=0)
            wnd.MouseDown = self.OnWndMouseDown
            tabs = [[mls.UI_SHARED_MYPETITIONS,
              wnd.sr.scroll,
              self,
              'mypetitions']]
            if self.GetIsPetitionee():
                tabs.append([mls.UI_SHARED_CLAIMEDPETITIONS,
                 wnd.sr.scroll,
                 self,
                 'claimedpetitions'])
                for each in self.GetQueues():
                    tabs.append([each.queueName,
                     wnd.sr.scroll,
                     self,
                     each.queueID])

            maintabs = uicls.TabGroup(name='tabparent', parent=wnd.sr.main, idx=0)
            maintabs.Startup(tabs, 'petitionspanel')
            wnd.SetMinSize([500, 256])
            wnd.sr.tabs = maintabs
        return wnd



    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.sr.scroll.ShowHint(hintstr)



    def OnWndMouseDown(self, *args):
        sm.GetService('neocom').BlinkOff('help')



    def RefreshSize(self, *args):
        pass



    def GetMyPetitions(self):
        if not self.mine:
            self.mine = sm.RemoteSvc('petitioner').GetMyPetitionsEx()
        return self.mine



    def ShowMyPetitions(self, *args):
        self.LogInfo('ShowMyPetitions')
        self.SetHint()
        groupid = 'mypetitions'
        tmplst = []
        mp = self.GetMyPetitions()
        owners = []
        for p in mp:
            if p.petitionerID not in owners:
                owners.append(p.petitionerID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        seenPetitions = {}
        scrolllist = []
        for p in mp:
            if not seenPetitions.has_key(p.petitionID):
                data = self.GetPetitionData('my', p)
                data.groupID = groupid
                data.p = p
                data.type = 'my'
                scrolllist.append(listentry.Get('PetitionField', data=data))
                seenPetitions[p.petitionID] = None

        wnd = self.GetWnd()
        if wnd:
            wnd.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_DATE,
             mls.UI_GENERIC_SUBJECT,
             mls.UI_GENERIC_STATUS,
             mls.UI_GENERIC_RATING,
             mls.UI_GENERIC_CATEGORY,
             mls.UI_SHARED_LASTUPDATE])
            if not len(scrolllist):
                self.SetHint(mls.UI_SHARED_YOUHAVENOPETITIONS)



    def ShowClaimedPetitions(self, *args):
        self.LogInfo('ShowClaimedPetitions')
        self.SetHint()
        groupid = 'claimedpetitions'
        mp = sm.RemoteSvc('petitioner').GetClaimedPetitions()
        owners = []
        for p in mp:
            if p.petitionerID not in owners:
                owners.append(p.petitionerID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        scrolllist = []
        for p in mp:
            data = self.GetPetitionData('claimed', p)
            data.groupID = groupid
            data.p = p
            data.type = 'claimed'
            scrolllist.append(listentry.Get('PetitionField', data=data))

        wnd = self.GetWnd()
        if wnd:
            wnd.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_DATE,
             mls.UI_GENERIC_SUBJECT,
             mls.UI_GENERIC_NAME,
             mls.UI_GENERIC_STATUS,
             mls.UI_GENERIC_UPDATED,
             mls.UI_GENERIC_CATEGORY,
             mls.UI_SHARED_LASTUPDATE])
            if not len(scrolllist):
                self.SetHint(mls.UI_SHARED_YOUHAVENOCLAIMEDPETITIONS)



    def ShowRating(self, *args):
        wnd = self.GetViewWnd()
        if not wnd or wnd.destroyed:
            return 
        p = wnd.sr.p
        main = wnd.sr.ratingparent
        uix.Flush(main)
        captionPar = uicls.Container(name='captionPar', parent=main, align=uiconst.TOTOP, width=const.defaultPadding)
        mainCaption = uicls.CaptionLabel(text=mls.UI_GENERIC_PETRATEHEADER, parent=captionPar, align=uiconst.RELATIVE, left=const.defaultPadding, top=8)
        captionPar.height = mainCaption.textheight + 16
        uicls.Container(name='push', parent=main, align=uiconst.TOLEFT, width=const.defaultPadding)
        uicls.Container(name='push', parent=main, align=uiconst.TORIGHT, width=const.defaultPadding)
        t1 = uicls.Label(text=mls.UI_GENERIC_PETRATESCALE, parent=main, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        currentRating = settings.user.ui.Get('petition_rating', None)
        currentResponseTimeRating = settings.user.ui.Get('petition_responseTimeRating', None)
        currentHelpfulnessRating = settings.user.ui.Get('petition_helpfulnessRating', None)
        currentAttitudeRating = settings.user.ui.Get('petition_attitudeRating', None)
        currentComment = settings.user.ui.Get('petition_ratingcomment', '')
        currentDateTime = getattr(p, 'ratingDateTime', None)
        cbParents = []
        if currentRating is not None:
            uicls.Label(text=mls.UI_GENERIC_PETRATEYOURRATING, parent=main, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            cbParent = uicls.Container(name='cbParent', parent=main, align=uiconst.TOTOP, height=32)
            left = 0
            for i in xrange(11):
                cb = uicls.Checkbox(text='', parent=cbParent, configName='rating', retval=i * 10, checked=currentRating == i * 10, groupname='rating', align=uiconst.CENTERLEFT, pos=(left,
                 0,
                 20,
                 18))
                cbtext = uicls.Label(text='%s' % i, parent=cbParent, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
                cbtext.left = cb.left + cb.width
                left = cbtext.left + cbtext.width + 4

            cbParents.append(cbParent)
        else:
            uicls.Label(text=mls.UI_GENERIC_PETRATERESPONSETIME, parent=main, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            cbParent = uicls.Container(name='cbResponseTimeParent', parent=main, align=uiconst.TOTOP, height=32)
            left = 0
            wnd.sr.responseTimeRatingCBs = []
            for i in xrange(11):
                cb = uicls.Checkbox(text='', parent=cbParent, configName='currentResponseTimeRating', retval=i * 10, checked=currentResponseTimeRating == i * 10, groupname='currentResponseTimeRating', align=uiconst.CENTERLEFT, pos=(left,
                 0,
                 20,
                 18), callback=self.OnCheckboxChange)
                cbtext = uicls.Label(text='%s' % i, parent=cbParent, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
                cbtext.left = cb.left + cb.width
                left = cbtext.left + cbtext.width + 4
                wnd.sr.responseTimeRatingCBs.append(cb)

            cbParents.append(cbParent)
            uicls.Label(text=mls.UI_GENERIC_PETRATEHELPFULNESS, parent=main, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            cbParent = uicls.Container(name='cbtHelpfulnessParent', parent=main, align=uiconst.TOTOP, height=32)
            left = 0
            wnd.sr.helpfulnessRatingCBs = []
            for i in xrange(11):
                cb = uicls.Checkbox(text='', parent=cbParent, configName='currentHelpfulnessRating', retval=i * 10, checked=currentHelpfulnessRating == i * 10, groupname='currentHelpfulnessRating', align=uiconst.CENTERLEFT, pos=(left,
                 0,
                 20,
                 18), callback=self.OnCheckboxChange)
                cbtext = uicls.Label(text='%s' % i, parent=cbParent, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
                cbtext.left = cb.left + cb.width
                left = cbtext.left + cbtext.width + 4
                wnd.sr.helpfulnessRatingCBs.append(cb)

            cbParents.append(cbParent)
            uicls.Label(text=mls.UI_GENERIC_PETRATEATTITUDE, parent=main, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            cbParent = uicls.Container(name='cbAttitudeParent', parent=main, align=uiconst.TOTOP, height=32)
            left = 0
            wnd.sr.attitudeRatingCBs = []
            for i in xrange(11):
                cb = uicls.Checkbox(text='', parent=cbParent, configName='currentAttitudeRating', retval=i * 10, checked=currentAttitudeRating == i * 10, groupname='currentAttitudeRating', align=uiconst.CENTERLEFT, pos=(left,
                 0,
                 20,
                 18), callback=self.OnCheckboxChange)
                cbtext = uicls.Label(text='%s' % i, parent=cbParent, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
                cbtext.left = cb.left + cb.width
                left = cbtext.left + cbtext.width + 4
                wnd.sr.attitudeRatingCBs.append(cb)

            cbParents.append(cbParent)
        wnd.sr.ratinghinttext = uicls.Label(text='', parent=main, autowidth=False, align=uiconst.TOTOP)
        t2 = uicls.Label(text=mls.UI_GENERIC_PETRATECOMMENT, parent=main, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        wnd.sr.ratingcomment = uicls.EditPlainText(setvalue=currentComment, parent=main, align=uiconst.TOALL, name='ratingcomment', maxLength=1000, padding=(-const.defaultPadding,
         4,
         -const.defaultPadding,
         0))
        (w, h,) = wnd.minsize
        wnd.SetMinSize([max(w, left + 12), 428], 1)
        if currentDateTime is None:
            wnd.sr.ratingcomment.OnFocusLost = self.OnTextEditChange
            uicls.ButtonGroup(btns=[[mls.UI_CMD_SUBMIT,
              self.SetRating,
              None,
              None]], parent=main, line=0, idx=0)
        else:
            for cbParent in cbParents:
                cbParent.state = uiconst.UI_DISABLED

            wnd.sr.ratingcomment.readonly = 1
            uicls.Label(text=mls.UI_GENERIC_PETRATETHANKS, parent=main, autowidth=False, align=uiconst.TOBOTTOM, idx=0, state=uiconst.UI_NORMAL)
            t1.state = uiconst.UI_HIDDEN
            t2.text = mls.UI_GENERIC_PETRATEYOURCOMMENTS
        wnd.sr.ratingtime = blue.os.GetTime()



    def OnCheckboxChange(self, *args):
        if not args:
            return 
        wnd = self.GetViewWnd()
        if wnd and not wnd.destroyed:
            settings.user.ui.Set('petition_%s' % args[0].name, args[0].data['value'])



    def OnTextEditChange(self, *args):
        if not args:
            return 
        wnd = self.GetViewWnd()
        if wnd and not wnd.destroyed:
            settings.user.ui.Set('petition_%s' % args[0].name, args[0].GetValue())



    def SetRating(self, *args):
        wnd = self.GetViewWnd()
        if not wnd or wnd.destroyed:
            return 
        p = wnd.sr.p
        currentRating = getattr(p, 'rating', None)
        currentComment = getattr(p, 'ratingComment', '')
        cbResponseTimeValue = [ cb for cb in wnd.sr.responseTimeRatingCBs if cb.checked ]
        if not cbResponseTimeValue:
            wnd.sr.ratinghinttext.text = mls.UI_GENERIC_PETRATENOTVALID
            return 
        responseTimeRating = cbResponseTimeValue[0].data['value']
        cbHelpfulnessValue = [ cb for cb in wnd.sr.helpfulnessRatingCBs if cb.checked ]
        if not cbHelpfulnessValue:
            wnd.sr.ratinghinttext.text = mls.UI_GENERIC_PETRATENOTVALID
            return 
        helpfulnessRating = cbHelpfulnessValue[0].data['value']
        cbAttitudeValue = [ cb for cb in wnd.sr.attitudeRatingCBs if cb.checked ]
        if not cbAttitudeValue:
            wnd.sr.ratinghinttext.text = mls.UI_GENERIC_PETRATENOTVALID
            return 
        attitudeRating = cbAttitudeValue[0].data['value']
        newComment = wnd.sr.ratingcomment.GetValue()
        if getattr(p, 'ratingDateTime', None):
            if currentRating != newRating or currentComment != newComment:
                sm.RemoteSvc('petitioner').UpdatePetitionRating(p.petitionID, responseTimeRating, helpfulnessRating, attitudeRating, newComment)
            else:
                return 
        else:
            sm.RemoteSvc('petitioner').AddPetitionRating(p.petitionID, responseTimeRating, helpfulnessRating, attitudeRating, newComment, wnd.sr.ratingtime)
        setattr(p, 'responseTimeRating', responseTimeRating)
        setattr(p, 'helpfulnessRating', helpfulnessRating)
        setattr(p, 'attitudeRating', attitudeRating)
        setattr(p, 'ratingComment', newComment)
        setattr(p, 'ratingDateTime', wnd.sr.ratingtime)
        settings.user.ui.Set('petition_responseTimeRating', responseTimeRating)
        settings.user.ui.Set('petition_helpfulnessRating', helpfulnessRating)
        settings.user.ui.Set('petition_attitudeRating', attitudeRating)
        settings.user.ui.Set('petition_ratingComment', newComment)
        self._ReloadVisible()
        uthread.new(self.ShowRating)



    def ShowPetitionQueue(self, queueID):
        if not self.GetIsPetitionee():
            return 
        self.LogInfo('ShowPetitionQueue %s' % queueID)
        self.SetHint()
        groupid = 'quequedpetitions%d' % queueID
        mp = sm.RemoteSvc('petitioner').GetPetitionQueue(queueID)
        owners = []
        for p in mp:
            if p.petitionerID and p.petitionerID not in owners:
                owners.append(p.petitionerID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        scrolllist = []
        for p in mp:
            data = self.GetPetitionData('queue', p)
            data.groupID = groupid
            data.p = p
            data.type = 'queue'
            scrolllist.append(listentry.Get('PetitionField', data=data))

        wnd = self.GetWnd()
        if wnd:
            wnd.sr.scroll.Load(contentList=scrolllist, headers=[mls.UI_GENERIC_DATE,
             mls.UI_GENERIC_SUBJECT,
             mls.UI_GENERIC_NAME,
             mls.UI_GENERIC_STATUS,
             mls.UI_GENERIC_UPDATED,
             mls.UI_GENERIC_CATEGORY,
             mls.UI_SHARED_LASTUPDATE])
            if not len(scrolllist):
                self.SetHint(mls.UI_SHARED_THISQUEUEHASNOPETITIONS)



    def GetPetitionData(self, type, p):
        data = util.KeyVal()
        data.menu = []
        data.cstring = self.GetC_String(p.categoryID)
        label = util.FmtDate(p.createDate, 'ls')
        label += '<t>' + p.subject
        if type == 'queue' or type == 'claimed':
            if p.petitionerID:
                label += '<t>%s' % cfg.eveowners.Get(p.petitionerID).name
            else:
                label += '<t>%s' % p.email
            if p.claimed:
                label += '<t>' + mls.UI_SHARED_CLAIMED
                label += '<t>' + [mls.UI_GENERIC_UPDATED, mls.UI_GENERIC_WAITING][p.updated]
                data.menu.append((mls.UI_CMD_CLOSEPETITION, self.ClosePetition, (p.petitionID,)))
                data.menu.append((mls.UI_CMD_UNCLAIMPETITION, self.UnClaimPetition, (p.petitionID,)))
                if getattr(p, 'escalatesTo', None):
                    data.menu.append((mls.UI_CMD_ESCALATEPETITION, self.EscalatePetition, (p.petitionID, p.escalatesTo)))
            else:
                label += '<t>' + mls.UI_SHARED_UNCLAIMED
                label += '<t>-'
                if not p.closed and not p.deleted:
                    if p.petitionerID != session.charid:
                        data.menu.append((mls.UI_CMD_CLAIMPETITION2, self.ClaimPetition, (p,)))
        elif type == 'my':
            if p.closed:
                label += '<t>' + mls.UI_GENERIC_CLOSED
                rating = getattr(p, 'rating', None)
                if rating is not None:
                    label += '<t>%s' % (int(rating) / 10)
                else:
                    responseTimeRating = getattr(p, 'responseTimeRating', None)
                    helpfulnessRating = getattr(p, 'helpfulnessRating', None)
                    attitudeRating = getattr(p, 'attitudeRating', None)
                    if responseTimeRating is not None and helpfulnessRating is not None and attitudeRating is not None:
                        label += '<t>%s' % (int((responseTimeRating + helpfulnessRating + attitudeRating) / 3) / 10)
                    else:
                        rateable = getattr(p, 'rateable', 0)
                        if rateable:
                            label += '<t>' + mls.UI_GENERIC_NOTRATED
                        else:
                            label += '<t>-'
                data.menu.append((mls.UI_CMD_DELETEPETITION, self.DeletePetition, (p.petitionID,)))
                rateable = getattr(p, 'rateable', 0)
                if rateable:
                    currentDateTime = getattr(p, 'ratingDateTime', None)
                    if currentDateTime is None or currentDateTime + WEEK > blue.os.GetTime():
                        data.menu.append((mls.UI_CMD_RATE, self.RatePetition, (p,)))
            elif not p.claimed:
                label += '<t>' + mls.UI_GENERIC_OPEN
                data.menu.append((mls.UI_CMD_CANCELPETITION, self.CancelPetition, (p.petitionID,)))
            else:
                label += '<t>' + mls.UI_GENERIC_INACTION
            label += '<t>-'
        data.menu.insert(0, None)
        data.menu.insert(0, (mls.UI_CMD_VIEWPETITON, self.ShowPetition, (p,)))
        if type == 'my':
            label += '<t>%s<t>%s' % (data.cstring, util.FmtDate(p.touchDate, 'ls'))
        else:
            label += '<t>%s<t>-' % data.cstring
        data.label = label
        return data



    def RatePetition(self, p):
        viewwnd = self.ShowPetition(p)
        if viewwnd.sr.maintabs.GetSelectedArgs() != 'rating':
            uthread.new(viewwnd.sr.maintabs.ShowPanelByName, mls.UI_GENERIC_RATING)



    def GetQueues(self):
        if self.queues is None:
            if self.GetIsPetitionee():
                queues = sm.RemoteSvc('petitioner').GetQueues()
                for queue in queues:
                    queue.queueName = Tr(queue.queueName, 'dbo.petQueues.queueName', queue.queueID)

                self.queues = queues
        return self.queues



    def GetCategories(self):
        if self.categories is None:
            self.categories = sm.RemoteSvc('petitioner').GetCategories()
        return self.categories



    def GetCategory(self, id):
        for each in self.GetCategories():
            if each.categoryID == id:
                return each




    def GetC_String(self, id):
        cat = self.GetCategory(id)
        if cat:
            return cat.displayName
        return mls.UI_GENERIC_UNKNOWN



    def GetIsPetitionee(self):
        if self.petitionee is None:
            role = eve.session.role
            if role & service.ROLE_PETITIONEE == service.ROLE_PETITIONEE:
                self.petitionee = 1
                if role & service.ROLE_GMH == service.ROLE_GMH:
                    self.petitionee = 2
            else:
                self.petitionee = 0
        return self.petitionee



    def GetStatusName(self, p):
        status = ''
        if getattr(p, 'closed', 0) == 0:
            status = mls.UI_GENERIC_OPEN
            if p.claimed:
                status = mls.UI_GENERIC_INACTION
        else:
            status = mls.UI_GENERIC_CLOSED
        return status



    def NewPetition(self, *args):
        wnd = sm.GetService('window').GetWindow('petitionwindow', create=0, decoClass=form.PetitionWindow)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
        else:
            wnd = sm.GetService('window').GetWindow('petitionwindow', create=1, decoClass=form.PetitionWindow)
            wnd.CheckHeight()



    def OpenBrowser(self, *args):
        if args:
            blue.os.ShellExecute(args[0])



    def SelectionChange(self, selected):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        btnparent = wnd.sr.buttons.children[0]
        for btn in btnparent.children:
            btn.state = uiconst.UI_HIDDEN

        if selected:
            p = selected[0].p
            tab = wnd.sr.tabs.GetVisible(1)
            btnparent.children[0].state = uiconst.UI_NORMAL
            if tab.sr.args == 'claimedpetitions' or tab.sr.args in range(6):
                if not p.claimed and (p.closed or p.deleted or p.petitionerID != session.charid):
                    btnparent.children[1].state = uiconst.UI_NORMAL
            if tab.sr.args == 'mypetitions':
                if p.closed:
                    btnparent.children[2].state = uiconst.UI_NORMAL
                    rateable = getattr(p, 'rateable', 0)
                    if rateable:
                        currentDateTime = getattr(p, 'ratingDateTime', None)
                        if currentDateTime is None or currentDateTime + WEEK > blue.os.GetTime():
                            btnparent.children[4].state = uiconst.UI_NORMAL
                elif not p.claimed:
                    btnparent.children[3].state = uiconst.UI_NORMAL
            btnparent.width = sum([ btn.width for btn in btnparent.children if btn.state == uiconst.UI_NORMAL ])



    def ShowPetitionClicked(self, *args):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        selected = wnd.sr.scroll.GetSelected()
        if selected:
            self.ShowPetition(selected[0].p)



    def ClaimPetitionClicked(self, *args):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        selected = wnd.sr.scroll.GetSelected()
        if selected:
            self.ClaimPetition(selected[0].p)



    def DeletePetitionClicked(self, *args):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        selected = wnd.sr.scroll.GetSelected()
        if selected:
            self.DeletePetition(selected[0].p.petitionID)



    def CancelPetitionClicked(self, *args):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        selected = wnd.sr.scroll.GetSelected()
        if selected:
            self.CancelPetition(selected[0].p.petitionID)



    def RatePetitionClicked(self, *args):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return 
        selected = wnd.sr.scroll.GetSelected()
        if selected:
            viewwnd = self.ShowPetition(selected[0].p)
            uthread.new(self.OpenRateView, viewwnd)



    def OpenRateView(self, viewwnd):
        if viewwnd and viewwnd.sr.maintabs.GetSelectedArgs() != 'rating':
            viewwnd.sr.maintabs.ShowPanelByName(mls.UI_GENERIC_RATING)



    def CreatePetition(self, subject, petition, categoryID, retval, OocCharacterID):
        self.LogInfo('CreatePetition')
        combatLog = None
        chatLog = None
        messages = sm.GetService('LSC').GetChannelMessages()
        if len(messages):
            messageText = ''
            for m in messages:
                (t, mes,) = m
                messageText += '\\%s: %s\n' % (mls.UI_GENERIC_CHANNEL, t)
                for line in mes:
                    messageText += '[%s] %s> %s\n' % (util.FmtDate(line[3]), line[0], line[1])


            if messageText:
                chatLog = messageText
        if chatLog:
            chatLog = chatLog[(-const.petitionMaxChatLogSize):]
        combatLog = sm.GetService('logger').GetLog()
        if not sm.RemoteSvc('petitioner').CreatePetition(subject, petition, categoryID, retval, OocCharacterID, combatLog=combatLog, chatLog=chatLog):
            eve.Message('CannotPostPetition', {'text': mls.UI_SHARED_CANNOTPOSTPETITION4})
            return 
        self.mine = None
        if session.charid:
            self._ShowPanelByName(mls.UI_SHARED_MYPETITIONS)
        else:
            eve.Message('PetitionSuccess', {'text': ''})



    def GetViewWnd(self, new = 0):
        wnd = sm.GetService('window').GetWindow('petitionview')
        if not wnd and new:
            wnd = sm.GetService('window').GetWindow('petitionview', create=1)
            wnd.sr.main = uiutil.GetChild(wnd, 'main')
            wnd.scope = 'station_inflight'
            wnd.SetCaption(mls.UI_SHARED_VIEWPETITON)
            wnd.SetMinSize([340, 300])
            wnd.SetWndIcon('74_14')
            wnd.MakeUnResizeable()
            wnd.sr.scroll = uicls.Scroll(parent=wnd.sr.main, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            wnd.OnScale_ = self.OnViewScale
        return wnd



    def ShowPetition(self, p, *args):
        self.LogInfo('ShowPetition')
        viewwnd = self.GetViewWnd()
        if viewwnd and not viewwnd.destroyed:
            viewwnd.SelfDestruct()
        viewwnd = self.GetViewWnd(1)
        buttons = []
        status = self.GetStatusName(p)
        if self.GetIsPetitionee():
            if p.claimed:
                buttons.append({'caption': mls.UI_CMD_MESSAGE,
                 'function': self.SendMessage,
                 'args': p.petitionID})
                buttons.append({'caption': mls.UI_CMD_UNCLAIM,
                 'function': self.UnClaimPetition,
                 'args': p.petitionID})
                if getattr(p, 'escalatesTo', None):
                    buttons.append({'caption': mls.UI_CMD_ESCALATE,
                     'function': self.EscalatePetition,
                     'args': (p.petitionID, p.escalatesTo)})
                buttons.append({'caption': mls.UI_CMD_CLOSE,
                 'function': self.ClosePetition,
                 'args': p.petitionID})
            elif not p.deleted:
                if not p.closed:
                    if p.petitionerID != session.charid:
                        buttons.append({'caption': mls.UI_CMD_CLAIM,
                         'function': self.ClaimPetition,
                         'args': p})
                    else:
                        buttons.append({'caption': mls.UI_CMD_ADDMESSAGE,
                         'size': 'large',
                         'function': self.SendMessage,
                         'args': p.petitionID})
                else:
                    buttons.append({'caption': mls.UI_CMD_DELETE,
                     'function': self.DeletePetition,
                     'args': p.petitionID})
        elif not p.closed:
            buttons.append({'caption': mls.UI_CMD_ADDMESSAGE,
             'size': 'large',
             'function': self.SendMessage,
             'args': p.petitionID})
        else:
            buttons.append({'caption': mls.UI_CMD_DELETE,
             'function': self.DeletePetition,
             'args': p.petitionID})
        pet = ''
        if getattr(p, 'petition', None):
            pet = p.petition
        format = [{'type': 'push'},
         {'type': 'btline'},
         {'type': 'labeltext',
          'label': mls.UI_GENERIC_CATEGORY,
          'text': self.GetC_String(p.categoryID),
          'frame': 1},
         {'type': 'labeltext',
          'label': mls.UI_GENERIC_STATUS,
          'text': status,
          'frame': 1},
         {'type': 'labeltext',
          'label': mls.UI_GENERIC_SUBJECT,
          'text': p.subject,
          'frame': 1,
          'refreshheight': 1},
         {'type': 'push',
          'width': 20,
          'frame': 1},
         {'type': 'textedit',
          'label': '_hide',
          'text': pet.replace('\n', '<br>'),
          'readonly': 1,
          'height': 120,
          'frame': 1},
         {'type': 'push',
          'width': 20,
          'frame': 1}]
        if p.properties is not None:
            for pk in p.properties.iterkeys():
                for kv in p.properties[pk]:
                    format.append({'type': 'labeltext',
                     'label': Tr(kv, 'dbo.petCategoryProperties.k', pk),
                     'labelwidth': 140,
                     'text': p.properties[pk][kv],
                     'frame': 1})


        if len(buttons):
            format.append({'type': 'btline'})
            format.append({'type': 'btnonly',
             'buttons': buttons,
             'uniSize': 0})
            format.append({'type': 'push',
             'height': 8})
        (_form, retfields, reqresult, panels, errorcheck, refresh,) = sm.GetService('form').GetForm(format, xtriui.FormWnd(name='form', align=uiconst.TOTOP, parent=viewwnd.sr.main))
        _form.children.insert(0, uicls.Container(name='push', align=uiconst.TOLEFT, width=7))
        _form.children.insert(0, uicls.Container(name='push', align=uiconst.TORIGHT, width=7))
        viewformat = [{'type': 'push'},
         {'type': 'btnonly',
          'buttons': [{'caption': mls.UI_CMD_REPLY,
                       'align': 'left',
                       'function': self.SendMessage,
                       'args': p.petitionID}]},
         {'type': 'push'},
         {'type': 'push'},
         {'type': 'textedit',
          'label': '_hide',
          'key': 'body',
          'readonly': 1,
          'height': 120}]
        viewformparent = xtriui.FormWnd(name='form', align=uiconst.TOBOTTOM)
        viewwnd.sr.main.children.insert(0, viewformparent)
        (_viewform, viewretfields, viewreqresult, viewpanels, viewerrorcheck, viewrefresh,) = sm.GetService('form').GetForm(viewformat, viewformparent)
        _viewform.children.insert(0, uicls.Container(name='push', align=uiconst.TOLEFT, width=const.defaultPadding))
        _viewform.children.insert(0, uicls.Container(name='push', align=uiconst.TORIGHT, width=const.defaultPadding))
        _viewform.height += const.defaultPadding
        viewwnd.sr.viewmessageform = _viewform
        viewwnd.sr.viewmessageform.state = uiconst.UI_HIDDEN
        viewwnd.sr.refreshitems = viewrefresh
        viewwnd.sr.p = p
        viewwnd.SetMinSize([340, _form.top + _form.height + 100], 1)
        tabs = [[mls.UI_GENERIC_GENERALINFO,
          _form,
          self,
          'generic'], [mls.UI_GENERIC_MESSAGES,
          viewwnd.sr.scroll,
          self,
          'messages']]
        if p.closed:
            viewwnd.sr.ratingparent = uicls.Container(name='ratingparent', parent=viewwnd.sr.main, align=uiconst.TOALL, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
            uicls.Frame(parent=viewwnd.sr.ratingparent)
            tabs.append([mls.UI_GENERIC_RATING,
             viewwnd.sr.ratingparent,
             self,
             'rating'])
        if self.GetIsPetitionee():
            tabs.append([mls.UI_SHARED_LOG,
             viewwnd.sr.scroll,
             self,
             'logs'])
        viewwnd.sr.maintabs = uicls.TabGroup(name='tabparent', parent=viewwnd.sr.main, idx=0)
        viewwnd.sr.maintabs.Startup(tabs, 'viewpetition')
        settings.user.ui.Set('petition_rating', getattr(p, 'rating', None))
        settings.user.ui.Set('petition_responseTimeRating', getattr(p, 'responseTimeRating', None))
        settings.user.ui.Set('petition_helpfulnessRating', getattr(p, 'helpfulnessRating', None))
        settings.user.ui.Set('petition_attitudeRating', getattr(p, 'attitudeRating', None))
        settings.user.ui.Set('petition_ratingcomment', getattr(p, 'ratingComment', ''))
        return viewwnd



    def OnViewScale(self, *args):
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed:
            return 
        for each in viewwnd.sr.refreshitems:
            if hasattr(each, 'RefreshSize'):
                each.RefreshSize()




    def LoadLogs(self):
        if not self.GetIsPetitionee():
            return 
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed or self.loadinglogs:
            return 
        if viewwnd is not None and viewwnd.sr.viewmessageform:
            viewwnd.sr.viewmessageform.state = uiconst.UI_HIDDEN
        p = viewwnd.sr.p
        self.loadinglogs = 1
        plogs = sm.RemoteSvc('petitioner').GetLog(p.petitionID)
        texts = sm.RemoteSvc('petitioner').GetEvents()
        textDict = {}
        for row in texts:
            textDict[row.eventID] = row.eventText

        rowDescriptor = blue.DBRowDescriptor((('logDateTime', const.DBTYPE_FILETIME),
         ('characterID', const.DBTYPE_I4),
         ('userName', const.DBTYPE_WSTR),
         ('eventID', const.DBTYPE_UI1),
         ('eventText', const.DBTYPE_STR)))
        rowset = dbutil.CRowset(rowDescriptor, [])
        owners = []
        for pl in plogs:
            if pl.characterID is not None and pl.characterID not in owners:
                owners.append(pl.characterID)
            rowset.InsertNew([pl.logDateTime,
             pl.characterID,
             pl.userName,
             pl.eventID,
             textDict[pl.eventID]])

        if len(owners):
            cfg.eveowners.Prime(owners)
        scrolllist = []
        for pl in rowset:
            data = util.KeyVal()
            data.log = pl
            data.p = p
            scrolllist.append(listentry.Get('Logfield', data=data))

        viewwnd.sr.scroll.Load(fixedEntryHeight=24, contentList=scrolllist)
        self.loadinglogs = 0



    def LoadMessages(self):
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed or self.loadingmessages:
            return 
        p = viewwnd.sr.p
        viewwnd.sr.lastSender = 0
        self.loadingmessages = 1
        pmsgs = sm.RemoteSvc('petitioner').GetPetitionMessages(p.petitionID)
        owners = []
        for pm in pmsgs:
            if pm.senderID is not None and pm.senderID not in owners:
                owners.append(pm.senderID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        scrolllist = []
        for pm in pmsgs:
            if viewwnd.sr.lastSender == 0:
                viewwnd.sr.lastSender = pm.senderID
            data = util.KeyVal()
            data.msg = pm
            data.p = p
            scrolllist.append(listentry.Get('MessageField', data=data))

        viewwnd.sr.scroll.Load(contentList=scrolllist)
        self.loadingmessages = 0



    def ShowMessage(self, msg, p):
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed:
            return 
        viewwnd.ShowLoad()
        if viewwnd.sr.lastSender == session.charid or p.closed == 1:
            viewwnd.sr.viewmessageform.children[3].state = uiconst.UI_HIDDEN
        uiutil.Update(viewwnd, 'Petition::ShowMessage')
        viewwnd.sr.viewmessageform.sr.body.SetValue(msg.text.replace('\n', '<br>'), scrolltotop=1)
        viewwnd.sr.viewmessageform.state = uiconst.UI_PICKCHILDREN
        self.MarkAsRead(msg.messageID)
        viewwnd.HideLoad()



    def SendMessage(self, petitionid, *args):
        format = [{'type': 'textedit',
          'height': 128,
          'label': '_hide',
          'key': 'message',
          'frame': 0,
          'maxlength': 1000}, {'type': 'push',
          'height': 14}]
        if self.GetIsPetitionee():
            format.append({'type': 'checkbox',
             'required': 0,
             'height': 32,
             'setvalue': 0,
             'key': 'comment',
             'label': '',
             'text': mls.UI_SHARED_ADDTHISMESSAGEASCOMMENT})
        retval = uix.HybridWnd(format, mls.UI_CMD_SENDMESSAGE, 1, 'sendMessage', None, None, 340, 256, blockconfirm=1)
        if retval is not None:
            message = retval['message']
            if message == '':
                return 
            if self.GetIsPetitionee():
                comment = retval['comment']
                try:
                    sm.RemoteSvc('petitioner').PetitioneeChat(petitionid, message, comment)
                except UserError as e:
                    if e.msg != 'PetitionClosed':
                        raise 
                    eve.Message('MessageNotSentPetitionAlreadyClosed')
                    sys.exc_clear()
            else:
                try:
                    sm.RemoteSvc('petitioner').PetitionerChat(petitionid, message)
                except UserError as e:
                    if e.msg != 'PetitionClosed':
                        raise 
                    eve.Message('MessageNotSentPetitionAlreadyClosed')
                    sys.exc_clear()



    def OnPetitionMessage(self, petitionID, charID, messageText, messageID):
        if eve.session.charid is None:
            return 
        viewwnd = self.GetViewWnd()
        self.mine = None
        if charID != session.charid and (viewwnd is None or viewwnd.destroyed):
            if self.GetIsPetitionee():
                characterName = charName = cfg.eveowners.Get(charID).name
                eve.Message('PetPetioneeGotResposne', {'characterName': characterName})
            else:
                self.NewMessage(petitionID, messageText.replace('\n', '<br>'), messageID)
        else:
            self.LoadMessages()
        sm.GetService('neocom').Blink('help')



    def SendMessageOpen(self, sender, *args):
        self.LogInfo('SendMessageOpen')
        message = sender.text
        if message != '':
            sender.text = ''
            petitionid = sender.data['key']
            try:
                sm.RemoteSvc('petitioner').PetitionerChat(petitionid, message)
            except UserError as e:
                if e.msg != 'PetitionClosed':
                    raise 
                eve.Message('MessageNotSentPetitionAlreadyClosed')
                sys.exc_clear()



    def SendMessageClaimed(self, sender, *args):
        self.LogInfo('SendMessageClaimed')
        message = sender.text
        if message != '':
            sender.text = ''
            petitionid = sender.data['key']
            try:
                sm.RemoteSvc('petitioner').PetitioneeChat(petitionid, message)
            except UserError as e:
                if e.msg != 'PetitionClosed':
                    raise 
                eve.Message('MessageNotSentPetitionAlreadyClosed')
                sys.exc_clear()



    def CloseViewWindow(self, *args):
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed:
            return 
        viewwnd.SelfDestruct()



    def DeletePetition(self, petitionid, *args):
        self.LogInfo('DeletePetition')
        if eve.Message('PetitionQuestion2', {}, uiconst.YESNO) == uiconst.ID_YES:
            ret = sm.RemoteSvc('petitioner').DeletePetition(petitionid)
            self._ShowPanelByName(mls.UI_SHARED_MYPETITIONS)
            viewwnd = self.GetViewWnd()
            if viewwnd is None or viewwnd.destroyed:
                return 
            viewwnd.SelfDestruct()



    def CancelPetition(self, petitionid, *args):
        self.LogInfo('CancelPetition')
        if eve.Message('PetitionQuestion3', {}, uiconst.YESNO) == uiconst.ID_YES:
            sm.RemoteSvc('petitioner').CancelPetition(petitionid)
            self.mine = None
            self._ShowPanelByName(mls.UI_SHARED_MYPETITIONS)
            viewwnd = self.GetViewWnd()
            if viewwnd is None or viewwnd.destroyed:
                return 
            viewwnd.SelfDestruct()



    def ClosePetition(self, petitionid, *args):
        self.LogInfo('ClosePetition')
        sm.RemoteSvc('petitioner').ClosePetition(petitionid)
        self._ShowPanelByName(mls.UI_SHARED_CLAIMEDPETITIONS)
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed:
            return 
        viewwnd.SelfDestruct()



    def UnClaimPetition(self, petitionid, *args):
        self.LogInfo('UnClaimPetition')
        sm.RemoteSvc('petitioner').UnClaimPetition(petitionid)
        self._ShowPanelByName(mls.UI_SHARED_CLAIMEDPETITIONS)
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed:
            return 
        viewwnd.SelfDestruct()



    def EscalatePetition(self, postArgs, *args):
        if type(postArgs) != type(()):
            postArgs = (postArgs,) + args
        (petitionid, escalatesTo,) = postArgs
        self.LogInfo('UnClaimPetition')
        sm.RemoteSvc('petitioner').EscalatePetition(petitionid, escalatesTo)
        self._ShowPanelByName(mls.UI_SHARED_CLAIMEDPETITIONS)
        viewwnd = self.GetViewWnd()
        if viewwnd is None or viewwnd.destroyed:
            return 
        viewwnd.SelfDestruct()



    def ClaimPetition(self, p, *args):
        self.LogInfo('ClaimPetition')
        if sm.RemoteSvc('petitioner').ClaimPetition(p.petitionID) > 0:
            viewwnd = self.GetViewWnd()
            if viewwnd is not None and not viewwnd.destroyed:
                viewwnd.SelfDestruct()
            p.claimed = 1
            self.ShowPetition(p)
            self._ShowPanelByName(mls.UI_SHARED_CLAIMEDPETITIONS)
        else:
            eve.Message('PetitionInfo1')



    def _ShowPanelByName(self, panelName, *args):
        self.mine = None
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.tabs.ShowPanelByName(panelName)



    def _ReloadVisible(self, *args):
        self.mine = None
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.tabs.ReloadVisible()




class LogField(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.Logfield'

    def Startup(self, *args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.icon = uicls.Icon(parent=self, pos=(-2, -1, 26, 26), name='icon', state=uiconst.UI_DISABLED, icon='ui_9_64_1', ignoreSize=True, align=uiconst.RELATIVE)
        self.sr.selection = uicls.Fill(parent=self, padding=(0, 1, 0, 1), name='selection', state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
        self.selection = None
        self.sr.subject = uicls.Label(text='', parent=self, left=26, top=2, letterspace=1, fontsize=10, state=uiconst.UI_DISABLED, uppercase=1, tabs=[200, 500])
        self.state = uiconst.UI_NORMAL



    def Load(self, node):
        self.sr.node = node
        data = node
        self.log = data.log
        self.p = data.p
        charName = ''
        if self.log.characterID:
            charName = cfg.eveowners.Get(self.log.characterID).name
        self.sr.subject.text = '%s<t>%s<br>%s<t>%s' % (util.FmtDate(self.log.logDateTime),
         charName,
         self.log.eventText,
         self.log.userName)
        if node.Get('selected', 0):
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN



    def GetHeight(_self, *args):
        (node, width,) = args
        theight = uix.GetTextHeight('X<br>X', autoWidth=1, fontsize=10, hspace=1, uppercase=1)
        node.height = max(24, theight + 4)
        return node.height




class MessageField(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.MessageField'

    def Startup(self, *args):
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.icon = uicls.Icon(parent=self, pos=(-2, -1, 26, 26), name='icon', state=uiconst.UI_DISABLED, icon='ui_9_64_2', ignoreSize=True, align=uiconst.RELATIVE)
        self.sr.selection = uicls.Fill(parent=self, padding=(0, 1, 0, 1), name='selection', state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
        self.selection = None
        self.sr.subject = uicls.Label(text='', parent=self, left=26, top=2, letterspace=1, fontsize=10, state=uiconst.UI_DISABLED, uppercase=1, tabs=[120, 500])
        self.state = uiconst.UI_NORMAL



    def Load(self, node):
        self.sr.node = node
        data = node
        self.msg = data.msg
        self.p = data.p
        self.sr.subject.text = '%s<br>%s' % (cfg.eveowners.Get(self.msg.senderID).name, util.FmtDate(self.msg.sentDate))
        if node.Get('selected', 0):
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN
        if self.msg.senderID == session.charid:
            self.sr.icon.LoadIcon('ui_7_64_14', True)
        else:
            self.sr.icon.LoadIcon('ui_6_64_4', True)
        if self.msg.comment == 1:
            self.sr.icon.LoadIcon('ui_9_64_2', True)



    def GetHeight(self, *args):
        (node, width,) = args
        theight = uix.GetTextHeight('X<br>X', autoWidth=1, fontsize=10, hspace=1, uppercase=1)
        node.height = max(24, theight + 4)
        return node.height



    def _OnClose(self):
        self.msg = None
        self.p = None
        self.selection = None



    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        sm.StartService('petition').ShowMessage(self.msg, self.p)



    def GetMenu(self):
        return [(mls.UI_CMD_VIEWMESSAGE, sm.StartService('petition').ShowMessage, (self.msg, self.p))]




class PetitionField(listentry.Generic):
    __guid__ = 'listentry.PetitionField'
    __notifyevents__ = ['OnContactLoggedOn', 'OnContactLoggedOff']

    def OnContactLoggedOn(self, charID):
        if self.sr.node and charID == self.sr.node.p.petitionerID:
            self.SetOnline(1)



    def OnContactLoggedOff(self, charID):
        if self.sr.node and charID == self.sr.node.p.petitionerID:
            self.SetOnline(0)



    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        if node.type != 'my':
            self.SetOnline(getattr(node.p, 'isOnline', 0))
        elif self.sr.Get('onlinestatus', None):
            self.sr.onlinestatus.state = uiconst.UI_HIDDEN



    def GetMenu(self):
        self.OnClick()
        return self.sr.node.menu



    def SetOnline(self, online):
        if not self.sr.Get('onlinestatus', None):
            self.sr.onlinestatus = uicls.Fill(parent=self, width=8, align=uiconst.TORIGHT, color=(1.0, 1.0, 1.0, 0.75), idx=4)
        color = (0.5, 0.0, 0.0)
        if online == 1:
            color = (0.0, 0.5, 0.0)
        if online == 2:
            color = (0.5, 0.25, 0.0)
        self.sr.onlinestatus.color.SetRGB(*color)
        self.sr.onlinestatus.state = uiconst.UI_DISABLED



    def OnDblClick(self, *args):
        p = self.sr.node.p
        sm.StartService('petition').ShowPetition(p)



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = max(24, uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 4)
        return node.height




class PetitionWindow(uicls.Window):
    __guid__ = 'form.PetitionWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(mls.UI_SHARED_PETITIONS)
        self.SetWndIcon('74_14')
        self.SetMinSize([350, 200])
        self.SetTopparentHeight(62)
        self.sr.formWindow = xtriui.FormWnd(name='form', align=uiconst.TOALL, parent=self.sr.main)
        self.sr.main.top = const.defaultPadding
        self.sr.mainCaption = uicls.CaptionLabel(text=mls.UI_CMD_CREATENEWPETITION, parent=self.sr.topParent, align=uiconst.RELATIVE, left=64, top=16)
        self.CategoryScreen()



    def CategoryScreen(self):
        self.sr.formWindow.Flush()
        format = [{'type': 'btline'}, {'type': 'push',
          'frame': 1}]
        self.GetFromSelect = 0
        self.OocCharacterID = None
        if not session.charid:
            if self.OocCharacterID == None:
                chars = sm.RemoteSvc('charUnboundMgr').GetCharacterInfo()
                first = 1
                self.GetFromSelect = 1
                format.append({'type': 'text',
                 'text': mls.UI_CHARSEL_SELECTCHARACTER,
                 'frame': 1})
                for char in chars:
                    format.append({'type': 'checkbox',
                     'required': 1,
                     'group': 'OocCharacter',
                     'height': 16,
                     'setvalue': first,
                     'key': char.characterID,
                     'label': '',
                     'text': char.characterName,
                     'frame': 1})
                    first = 0

                format.append({'type': 'push',
                 'frame': 1})
                format.append({'type': 'btline'})
                format.append({'type': 'push',
                 'frame': 1})
        (self.superCategories, self.childCategories, self.descriptions,) = self.GetCategories()
        format.append({'type': 'combo',
         'required': 1,
         'frame': 1,
         'key': 'superCategoryID',
         'label': mls.UI_GENERIC_GROUP,
         'options': self.superCategories,
         'callback': self.SuperCategorySelection})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'combo',
         'required': 1,
         'frame': 1,
         'key': 'subCategory',
         'label': mls.UI_GENERIC_CATEGORY,
         'options': [[mls.UI_PETITION_SELECTGROUP, None]],
         'callback': self.SubCategorySelection})
        format.append({'type': 'btnonly',
         'frame': 1,
         'buttons': [{'caption': mls.UI_CMD_SELECT,
                      'function': self.ConfirmCategory}]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        format.append({'type': 'push'})
        self.sr.formData = sm.GetService('form').GetForm(format, self.sr.formWindow)
        uicls.Container(name='push', parent=self.sr.formWindow, align=uiconst.TOLEFT, width=6)
        uicls.Container(name='push', parent=self.sr.formWindow, align=uiconst.TORIGHT, width=6)
        category = self.sr.formData[0].sr.subCategory.GetValue()
        if category:
            self.sr.mainText = uicls.Label(text=self.descriptions[category][0], parent=self.sr.formWindow, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_NORMAL)
        else:
            self.sr.mainText = uicls.Label(text='', parent=self.sr.formWindow, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_NORMAL)
        self.CheckHeight()



    def SubCategorySelection(self, combo, header, value, *args):
        if value != None:
            if combo.name == 'subCategory':
                ops = self.descriptions[value[0]]
            self.sr.mainText.text = ops
            self.CheckHeight()



    def CheckHeight(self):
        totalHeight = sum([ each.height for each in self.sr.formData[0].children if each.align == uiconst.TOTOP ])
        (mw, mh,) = self.minsize
        mh = totalHeight + self.sr.headerParent.height + self.sr.topParent.height + 20
        self.SetMinSize([mw, mh], 1)



    def SuperCategorySelection(self, combo, header, value, *args):
        if combo.name == 'superCategoryID' and value != None:
            ops = self.childCategories[value]
            hints = {}
            for (k, v,) in ops:
                hints[k] = self.descriptions[v[0]]

            self.sr.formData[0].sr.subCategory.LoadOptions(ops, hints=hints)
            current = self.sr.formData[0].sr.subCategory.GetValue()
            ops = self.descriptions[current[0]]
            self.sr.mainText.text = ops
            self.CheckHeight()



    def ConfirmCategory(self, *args):
        result = sm.GetService('form').ProcessForm(self.sr.formData[1], self.sr.formData[2])
        if result:
            self.category = result['subCategory']
            if self.GetFromSelect:
                self.OocCharacterID = result['OocCharacter']
            uthread.new(self.InputPetition)



    def InputPetition(self, *args):
        categoryID = self.category[0]
        categoryName = self.category[1]
        OocCharacterID = self.OocCharacterID
        can = sm.RemoteSvc('petitioner').MayPetition(categoryID, OocCharacterID)
        if can < 0:
            if can == -1:
                eve.Message('CannotPostPetition', {'text': mls.UI_SHARED_CANNOTPOSTPETITION1})
                return 
            if can == -2:
                eve.Message('CannotPostPetition', {'text': mls.UI_SHARED_CANNOTPOSTPETITION2 % {'max': const.maxPetitionsPerDay}})
                return 
            if can == -3:
                eve.Message('CannotPostPetition', {'text': mls.UI_SHARED_CANNOTPOSTPETITION3})
                return 
            if can == -4:
                eve.Message('CannotPostPetition', {'text': mls.UI_SHARED_CANNOTPOSTPETITION4})
                return 
            if can == -6:
                eve.Message('CannotPostPetition', {'text': mls.UI_SHARED_CANNOTPOSTPETITION6})
                return 
            if can == -7:
                eve.Message('CannotPostPetition', {'text': mls.UI_SHARED_CANNOTPOSTPETITION7})
            return 
        self.sr.formWindow.Flush()
        format = []
        format.append({'type': 'header',
         'text': categoryName,
         'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        self.properties = sm.RemoteSvc('petitioner').GetCategoryProperties(self.category[0])
        for property in self.properties:
            required = property.required
            format.append({'type': 'labeltext',
             'text': Tr(property.description, 'dbo.petProperties.description', property.propertyID),
             'frame': 1})
            if property.inputType == 'DropDown':
                populationInfo = sm.RemoteSvc('petitioner').PropertyPopulationInfo(property.inputInfo, self.OocCharacterID)
                populationInfo = self.FormatForDropDown(populationInfo)
                format.append({'type': 'combo',
                 'required': required,
                 'frame': 1,
                 'key': property.propertyName,
                 'options': populationInfo})
            if property.inputType == 'Picker':
                format.append({'type': 'edit',
                 'key': property.propertyName,
                 'maxLength': 200,
                 'height': 28,
                 'required': required,
                 'frame': 1})
                format.append({'type': 'labeltext',
                 'frame': 1,
                 'text': mls.UI_PETITION_MUSTSEARCH})
                format.append({'type': 'btnonly',
                 'frame': 1,
                 'buttons': [{'caption': mls.UI_CMD_SEARCH,
                              'function': self.PopulatePicker,
                              'args': property.propertyName}]})
            if property.inputType == 'EditBox':
                format.append({'type': 'edit',
                 'key': property.propertyName,
                 'setvalue': property.inputInfo,
                 'maxLength': 200,
                 'height': 28,
                 'required': required,
                 'frame': 1})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'btline'})

        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'key': 'subject',
         'label': mls.UI_GENERIC_SUBJECT,
         'maxLength': 200,
         'required': 1,
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'petition',
         'label': mls.UI_PETITION_PETITIONTEXT,
         'maxLength': 10000,
         'height': 300,
         'required': 1,
         'frame': 1})
        format.append({'type': 'btnonly',
         'frame': 1,
         'buttons': [{'caption': mls.UI_CMD_SUBMIT,
                      'function': self.CreatePetition}]})
        format.append({'type': 'btnonly',
         'frame': 1,
         'buttons': [{'caption': mls.UI_CMD_BACK,
                      'function': self.GoBack}]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        self.sr.mainText = uicls.Label(text=self.descriptions[categoryID], parent=self.sr.formWindow, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_NORMAL)
        self.sr.formData = sm.GetService('form').GetForm(format, self.sr.formWindow)
        self.CheckHeight()
        self.lockPetitioning = False



    def GoBack(self, *args):
        ret = eve.Message('AskAreYouSure', {'cons': mls.UI_PETITION_LOSEINFO}, uiconst.YESNO, default=uiconst.ID_NO)
        if ret == uiconst.ID_YES:
            self.CategoryScreen()



    def PopulatePicker(self, *args):
        elementName = args[0]
        filterString = sm.GetService('form').ProcessForm(self.sr.formData[1], [])[elementName]
        if len(filterString) >= 3:
            populationRecords = sm.RemoteSvc('petitioner').GetClientPickerInfo(filterString, elementName)
            picker = self.sr.formData[0].sr.Get(elementName)
            if len(populationRecords) > 0:
                picker.LoadCombo(elementName, populationRecords, None, None)
                picker.SetValue(str(populationRecords[0][1]))
                picker.SetText(populationRecords[0][0])
                if len(populationRecords) >= 25:
                    eve.Message('CustomInfo', {'info': mls.UI_PETITION_NARROWSEARCH})
            else:
                picker.SetText(mls.REPORT_INFONOTFOUND)
        else:
            eve.Message('CustomInfo', {'info': mls.UI_SHARED_PLEASETYPE3LETTERS})



    def FormatForDropDown(self, entryList):
        newList = []
        for entry in entryList:
            newList.append([entry[1], entry[0]])

        return newList



    def CreatePetition(self, *args):
        if self.lockPetitioning == True:
            return 
        self.lockPetitioning = True
        propertyList = []
        resultDict = sm.GetService('form').ProcessForm(self.sr.formData[1], self.sr.formData[2])
        combatLog = None
        chatLog = None
        categoryID = self.category[0]
        if resultDict:
            messages = sm.GetService('LSC').GetChannelMessages()
            if len(messages):
                messageText = ''
                for m in messages:
                    (t, mes,) = m
                    messageText += '\\%s: %s\n' % (mls.UI_GENERIC_CHANNEL, t)
                    for line in mes:
                        messageText += '[%s] %s> %s\n' % (util.FmtDate(line[3]), line[0], line[1])


                if messageText:
                    chatLog = messageText
            combatLog = sm.GetService('logger').GetLog()
            if chatLog:
                chatLog = chatLog[(-const.petitionMaxChatLogSize):]
            if combatLog:
                combatLog = combatLog[(-const.petitionMaxCombatLogSize):]
            for propertyRow in self.properties:
                if propertyRow.inputType == 'Picker':
                    value = self.sr.formData[0].sr.Get(propertyRow.propertyName).GetComboValue()
                    propertyList.append([propertyRow.propertyID, value])
                else:
                    propertyList.append([propertyRow.propertyID, resultDict[propertyRow.propertyName]])

            subject = resultDict['subject']
            petition = resultDict['petition']
            sm.RemoteSvc('petitioner').CreatePetition(subject, petition, categoryID, None, self.OocCharacterID, chatLog, combatLog, propertyList)
            sm.ScatterEvent('OnPetitionCreated')
            eve.Message('CustomInfo', {'info': mls.UI_PETITION_PETCREATED})
            self.CloseX()
        else:
            self.lockPetitioning = False



    def GetCategories(self):
        (parentCategoryDict, childCategoryDict, descriptionDict,) = sm.RemoteSvc('petitioner').GetCategoryHierarchicalInfo()
        parentCategories = [[mls.UI_PETITION_SELECT_PARENT_CATEGORY, None]]
        childCategoryRetDict = {}
        descriptions = []
        for parentID in parentCategoryDict:
            parentCategories.append((parentCategoryDict[parentID], parentID))

        for childGroupID in childCategoryDict:
            childGroupDict = childCategoryDict[childGroupID]
            childCategories = []
            for childID in childGroupDict:
                childCategories.append((childGroupDict[childID], (childID, childGroupDict[childID])))

            childCategoryRetDict[childGroupID] = childCategories

        return (parentCategories, childCategoryRetDict, descriptionDict)




