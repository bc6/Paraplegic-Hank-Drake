import util
import xtriui
import uix
import uiutil
import form
import listentry
import types
import uiconst
import uicls
import log

class CorpStandings(uicls.Container):
    __guid__ = 'form.CorpStandings'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnSetCorpStanding']

    def init(self):
        sm.RegisterNotify(self)



    def OnSetCorpStanding(self, *args):
        if uiutil.IsVisible(self) and self.sr.Get('inited', False) and self.sr.tabs:
            self.sr.tabs.ReloadVisible()



    def Load(self, args):
        if not self.sr.Get('inited', False):
            self.sr.inited = 1
            btns = None
            self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            if btns is not None:
                self.toolbarContainer.height = btns.height
            else:
                self.toolbarContainer.state = uiconst.UI_HIDDEN
            self.sr.contacts = form.ContactsForm(name='corpcontactsform', parent=self, pos=(0, 0, 0, 0))
            self.sr.contacts.Setup('corpcontact')
            self.sr.scroll = uicls.Scroll(name='standings', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
            self.sr.tabs.Startup([[mls.UI_CONTACTS_CORPCONTACTS,
              self.sr.contacts,
              self,
              'corpcontact'], [mls.UI_GENERIC_LIKEDBY,
              self.sr.scroll,
              self,
              'mystandings_to_positive'], [mls.UI_GENERIC_DISLIKEDBY,
              self.sr.scroll,
              self,
              'mystandings_to_negative']], 'corporationstandings', autoselecttab=1)
            return 
        sm.GetService('corpui').LoadTop('ui_7_64_6', mls.UI_CORP_STANDINGS)
        self.SetHint()
        if type(args) == types.StringType and args.startswith('mystandings_'):
            self.sr.standingtype = args
            if args == 'mystandings_to_positive':
                positive = True
            else:
                positive = False
            self.ShowStandings(positive)
        else:
            sm.GetService('addressbook').ShowContacts('corpcontact', self.sr.contacts)



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def ShowStandings(self, positive, *args):
        sm.GetService('corpui').ShowLoad()
        scrolllist = sm.GetService('standing').GetStandingEntries(positive, session.corpid)
        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist)
        sm.GetService('corpui').HideLoad()




class CorporationPickerDialog(uicls.Window):
    __guid__ = 'form.CorporationPickerDialog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.corporationID = None
        self.searchStr = ''
        self.playerCorpsOnly = 0
        self.SetScope('all')
        self.Confirm = self.ValidateOK
        strTitle = mls.UI_CORP_SELECTCORPORALLIANCE
        if self.playerCorpsOnly:
            strTitle = mls.UI_CORP_SELECTPLAYERCORP
        self.SetCaption(strTitle)
        self.SetMinSize([320, 300])
        self.SetWndIcon('ui_7_64_6')
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.standardBtns = uicls.ButtonGroup(btns=[[mls.UI_CMD_OK,
          self.OnOK,
          (),
          81], [mls.UI_CMD_CANCEL,
          self.OnCancel,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        self.label = uicls.Label(text=mls.UI_SHARED_TYPESEARCHSTR, parent=self.sr.topParent, left=70, top=16, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        inpt = uicls.SinglelineEdit(name='edit', parent=self.sr.topParent, left=70, top=self.label.top + self.label.height + 2, width=86, align=uiconst.TOPLEFT, maxLength=37)
        inpt.OnReturn = self.Search
        self.sr.inpt = inpt
        btn = uicls.Button(parent=self.sr.topParent, label=mls.UI_CMD_SEARCH, pos=(inpt.left + inpt.width + 2,
         inpt.top,
         0,
         0), func=self.Search, btn_default=1)



    def Search(self, *args):
        self.ShowLoad()
        scrolllist = []
        try:
            (groupID, exact,) = (const.groupCorporation, 0)
            self.searchStr = self.GetSearchStr()
            self.SetHint()
            if len(self.searchStr) < 1:
                self.SetHint(mls.UI_SHARED_PLEASETYPESOMETHING)
                return 
            result = sm.RemoteSvc('lookupSvc').LookupCorporationsOrAlliances(self.searchStr, exact)
            if result is None or not len(result):
                self.SetHint(mls.UI_CORP_HINT53 % {'search': self.searchStr})
                return 
            cfg.eveowners.Prime([ each.ownerID for each in result ])
            for each in result:
                owner = cfg.eveowners.Get(each.ownerID)
                scrolllist.append(listentry.Get('Item', {'label': owner.name,
                 'typeID': owner.typeID,
                 'itemID': each.ownerID,
                 'confirmOnDblClick': 1,
                 'listvalue': [owner.name, each.ownerID]}))


        finally:
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)
            self.HideLoad()




    def GetSearchStr(self):
        return self.sr.inpt.GetValue().strip()



    def Confirm(self):
        self.OnOK()



    def ValidateOK(self):
        if self.searchStr != self.GetSearchStr():
            self.Search()
            return 0
        log.LogInfo('ValidateOK')
        if self.corporationID is None:
            return 0
        return 1



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def OnOK(self, *args):
        sel = self.sr.scroll.GetSelected()
        if sel:
            self.corporationID = sel[0].itemID
            self.CloseX()
        else:
            self.SetHint(mls.UI_CORP_PLEASESELCORP)



    def OnCancel(self, *args):
        self.corporationID = None
        self.CloseX()




class CorporationOrAlliancePickerDailog(uicls.Window):
    __guid__ = 'form.CorporationOrAlliancePickerDailog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        warableEntitysOnly = attributes.warableEntitysOnly
        self.ownerID = None
        self.searchStr = ''
        self.warableEntitysOnly = warableEntitysOnly
        self.SetScope('all')
        self.Confirm = self.ValidateOK
        strTitle = mls.UI_CORP_SELCORPORALLIANCE
        if self.warableEntitysOnly:
            strTitle = mls.UI_CORP_SELWARABLECORPORALLIANCE
        self.SetCaption(strTitle)
        self.SetMinSize([320, 300])
        self.SetWndIcon('ui_7_64_6')
        self.sr.main = uiutil.GetChild(self, 'main')
        self.sr.standardBtns = uicls.ButtonGroup(btns=[[mls.UI_CMD_OK,
          self.OnOK,
          (),
          81], [mls.UI_CMD_CANCEL,
          self.OnCancel,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        self.sr.txtWarningContainer = uicls.Container(name='txtWarningContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN)
        self.sr.txtWarningContainerPad = uicls.Container(name='txtWarningCenteredContainer', parent=self.sr.txtWarningContainer, pos=(const.defaultPadding * 2,
         0,
         self.sr.main.width - const.defaultPadding * 4,
         0))
        self.sr.txtWarning = uicls.Label(text='', parent=self.sr.txtWarningContainerPad, align=uiconst.TOALL, top=0, color=[1,
         0,
         0,
         1], autowidth=False, autoheight=False, state=uiconst.UI_NORMAL)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, state=uiconst.UI_NORMAL)
        self.sr.scroll.multiSelect = False
        self.sr.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.label = uicls.Label(text=mls.UI_SHARED_TYPESEARCHSTR, parent=self.sr.topParent, left=70, top=5, fontsize=9, letterspace=2, uppercase=1, state=uiconst.UI_NORMAL)
        inpt = self.sr.inpt = uicls.SinglelineEdit(name='edit', parent=self.sr.topParent, left=70, top=self.label.top + self.label.height + 2, width=86, align=uiconst.TOPLEFT, maxLength=32)
        inpt.OnReturn = self.Search
        btn = uicls.Button(parent=self.sr.topParent, label=mls.UI_CMD_SEARCH, pos=(inpt.left + inpt.width + 2,
         inpt.top,
         0,
         0), func=self.Search, btn_default=1)
        self.sr.exactChkBox = uicls.Checkbox(text=mls.UI_SHARED_SEARCHEXACT, parent=self.sr.topParent, configName='SearchExactChk', retval=1, align=uiconst.TOPLEFT, pos=(inpt.left,
         inpt.top + inpt.height,
         200,
         0))
        return self



    def Search(self, *args):
        scrolllist = []
        self.ShowLoad()
        self.sr.txtWarningContainer.state = uiconst.UI_HIDDEN
        try:
            (groupID, exact,) = (const.groupCorporation, self.sr.exactChkBox.GetValue())
            self.searchStr = self.GetSearchStr()
            self.SetHint()
            if len(self.searchStr) < 1:
                self.SetHint(mls.UI_SHARED_PLEASETYPESOMETHING)
                return 
            result = sm.RemoteSvc('lookupSvc').LookupCorporationsOrAlliances(self.searchStr, exact, self.warableEntitysOnly)
            if result is None or not len(result):
                if exact:
                    self.SetHint(mls.UI_CORP_HINT54 % {'search': self.searchStr})
                else:
                    self.SetHint(mls.UI_CORP_HINT55 % {'search': self.searchStr})
                return 
            cfg.eveowners.Prime([ each.ownerID for each in result ])
            for each in result:
                owner = cfg.eveowners.Get(each.ownerID)
                scrolllist.append(listentry.Get('Item', {'label': owner.ownerName,
                 'OnDblClick': self.OnOK,
                 'typeID': owner.typeID,
                 'itemID': each.ownerID,
                 'confirmOnDblClick': 1,
                 'listvalue': [owner.ownerName, each.ownerID]}))


        finally:
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)
            self.HideLoad()




    def GetSearchStr(self):
        return self.sr.inpt.GetValue().strip()



    def Confirm(self):
        self.OnOK()



    def ValidateOK(self):
        if self.searchStr != self.GetSearchStr():
            self.Search()
            return 0
        log.LogInfo('ValidateOK')
        if self.ownerID is None:
            return 0
        return 1



    def SetHint(self, hintstr = None):
        if hintstr is not None:
            self.sr.txtWarning.text = hintstr
            self.sr.txtWarningContainer.state = uiconst.UI_DISABLED
            self.sr.txtWarningContainer.height = self.sr.txtWarning.textheight



    def HideHint(self):
        self.sr.txtWarningContainer.state = uiconst.UI_HIDDEN



    def OnScrollSelectionChange(self, *args):
        self.HideHint()



    def OnResizeUpdate(self, *args):
        self.sr.txtWarningContainer.height = self.sr.txtWarning.textheight



    def OnOK(self, *args):
        sel = self.sr.scroll.GetSelected()
        if sel:
            self.ownerID = sel[0].itemID
            self.CloseX()
        else:
            self.SetHint(mls.UI_GENERIC_PICKERROR2B % {'num': 1})



    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseX()




