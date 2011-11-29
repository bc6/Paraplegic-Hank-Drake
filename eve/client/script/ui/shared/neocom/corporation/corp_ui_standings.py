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
import localization

class CorpStandings(uicls.Container):
    __guid__ = 'form.CorpStandings'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnSetCorpStanding']

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
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
            self.sr.tabs.Startup([[localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/CorpContacts'),
              self.sr.contacts,
              self,
              'corpcontact'], [localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/LikedBy'),
              self.sr.scroll,
              self,
              'mystandings_to_positive'], [localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/DislikedBy'),
              self.sr.scroll,
              self,
              'mystandings_to_negative']], 'corporationstandings', autoselecttab=1)
            return 
        sm.GetService('corpui').LoadTop('ui_7_64_6', localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/CorpStandings'))
        self.SetHint()
        if type(args) == types.StringType and args.startswith('mystandings_'):
            self.sr.standingtype = args
            if args == 'mystandings_to_positive':
                positive = True
            else:
                positive = False
            self.ShowStandings(positive)
        else:
            self.sr.contacts.LoadContactsForm('corpcontact')



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def ShowStandings(self, positive, *args):
        sm.GetService('corpui').ShowLoad()
        scrolllist = sm.GetService('standing').GetStandingEntries(positive, session.corpid)
        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist)
        sm.GetService('corpui').HideLoad()




class CorporationOrAlliancePickerDailog(uicls.Window):
    __guid__ = 'form.CorporationOrAlliancePickerDailog'
    default_windowID = 'CorporationOrAlliancePickerDailog'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        warableEntitysOnly = attributes.warableEntitysOnly
        self.ownerID = None
        self.searchStr = ''
        self.warableEntitysOnly = warableEntitysOnly
        self.SetScope('all')
        self.Confirm = self.ValidateOK
        strTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/SelectCorpOrAlliance')
        if self.warableEntitysOnly:
            strTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/SelectWarableCorpOrAlliance')
        self.SetCaption(strTitle)
        self.SetMinSize([320, 300])
        self.SetWndIcon('ui_7_64_6')
        self.sr.main = uiutil.GetChild(self, 'main')
        self.sr.standardBtns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Generic/Cancel'),
          self.OnCancel,
          (),
          81]])
        self.sr.main.children.insert(0, self.sr.standardBtns)
        self.sr.txtWarningContainer = uicls.Container(name='txtWarningContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, height=32, padding=const.defaultPadding)
        self.sr.txtWarning = uicls.EveLabelMedium(text='', parent=self.sr.txtWarningContainer, align=uiconst.TOALL, top=0, color=[1,
         0,
         0,
         1], state=uiconst.UI_NORMAL)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, state=uiconst.UI_NORMAL)
        self.sr.scroll.multiSelect = False
        self.sr.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.label = uicls.EveLabelSmall(text=localization.GetByLabel('UI/Shared/TypeSearchString'), parent=self.sr.topParent, left=70, top=5, state=uiconst.UI_NORMAL)
        inpt = self.sr.inpt = uicls.SinglelineEdit(name='edit', parent=self.sr.topParent, left=70, top=self.label.top + self.label.height + 2, width=86, align=uiconst.TOPLEFT, maxLength=32)
        inpt.OnReturn = self.Search
        btn = uicls.Button(parent=self.sr.topParent, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/Search'), pos=(inpt.left + inpt.width + 2,
         inpt.top,
         0,
         0), func=self.Search, btn_default=1)
        self.sr.exactChkBox = uicls.Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/SearchExact'), parent=self.sr.topParent, configName='SearchExactChk', retval=1, align=uiconst.TOPLEFT, pos=(inpt.left,
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
                self.SetHint(localization.GetByLabel('UI/Shared/PleaseTypeSomething'))
                return 
            result = sm.RemoteSvc('lookupSvc').LookupCorporationsOrAlliances(self.searchStr, exact, self.warableEntitysOnly)
            if result is None or not len(result):
                if exact:
                    self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/ExactCorpOrAllianceNameNotFound', searchString=self.searchStr))
                else:
                    self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/CorpOrAllianceNameNotFound', searchString=self.searchStr))
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



    def HideHint(self):
        self.sr.txtWarningContainer.state = uiconst.UI_HIDDEN



    def OnScrollSelectionChange(self, *args):
        self.HideHint()



    def OnOK(self, *args):
        sel = self.sr.scroll.GetSelected()
        if sel:
            self.ownerID = sel[0].itemID
            self.CloseByUser()
        else:
            self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/ErrorPleaseChoose'))



    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseByUser()




