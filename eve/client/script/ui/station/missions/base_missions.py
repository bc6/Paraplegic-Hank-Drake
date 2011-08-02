import base
import blue
import draw
import form
import lg
import listentry
import log
import moniker
import service
import sys
import uix
import uiutil
import uthread
import util
import xtriui
import uicls
import uiconst

class BountyWindow(uicls.Window):
    __guid__ = 'form.BountyWindow'
    default_width = 400
    default_height = 300

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.bounties = None
        self.bountyCacheTimer = 0
        self.placebountycharid = None
        self.SetWndIcon('61_2', mainTop=-8)
        self.SetMinSize([350, 270])
        self.SetCaption(mls.UI_STATION_BOUNTY)
        self.label = uicls.WndCaptionLabel(text=' ', subcaption=' ', parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.scope = 'station'
        self.sr.tabs = uicls.TabGroup(name='tabparent', parent=self.sr.main, idx=1)
        self.sr.searchcontainer = uicls.Container(name='searchcontainer', align=uiconst.TOTOP, parent=self.sr.main, height=36, idx=1)
        self.sr.inpt = inpt = uicls.SinglelineEdit(name='search', parent=self.sr.searchcontainer, maxLength=32, left=5, top=17, width=86, label=mls.UI_SHARED_TYPESEARCHSTR)
        btn = uicls.Button(parent=self.sr.searchcontainer, label=mls.UI_CMD_SEARCH, pos=(inpt.left + inpt.width + 2,
         inpt.top,
         0,
         0), func=self.SearchCharacterFromBtn, btn_default=1)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        tabs = ([mls.UI_GENERIC_MOSTWANTED,
          self.sr.main,
          self,
          'browsebounties'], [mls.UI_GENERIC_PLACEBOUNTY,
          self.sr.main,
          self,
          'placebounty',
          self.sr.searchcontainer])
        self.sr.tabs.Startup(tabs, 'bountymissiontabs')



    def Load(self, key):
        self.label.text = mls.UI_STATION_BOUNTY
        if self and not self.destroyed:
            if key == 'placebounty':
                self.label.SetSubcaption(mls.UI_STATION_TEXT35 % {'isk': util.FmtISK(5000)})
                self.PlaceBounty()
            elif key == 'browsebounties':
                self.label.SetSubcaption(mls.UI_STATION_DELAYED2HOURS)
                self.BrowseBounties()



    def PlaceBounty(self):
        if self.placebountycharid is None:
            self.sr.scroll.Load(contentList=[], noContentHint=mls.UI_MARKET_PLEASETYPEANDSEARCH)
        else:
            self.SearchCharacter(self.placebountycharid)



    def BrowseBounties(self):
        bounties = sm.RemoteSvc('charMgr').GetTopBounties()
        cfg.eveowners.Prime([ b.characterID for b in bounties ])
        scrolllist = []
        for bounty in bounties:
            scrolllist.append(listentry.Get('User', {'charID': bounty.characterID,
             'bounty': bounty}))

        if not self or self.destroyed:
            return 
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=scrolllist, noContentHint=mls.UI_SHARED_NOBOUNTIES)



    def SearchCharacterFromBtn(self, *args):
        self.SearchCharacter()



    def SearchCharacter(self, charID = None, *args):
        import types
        sm.GetService('loading').Cycle(mls.UI_GENERIC_SEARCHING, self.sr.inpt.GetValue().strip())
        charID = charID or uix.Search(self.sr.inpt.GetValue().strip().lower(), const.groupCharacter, hideNPC=1, getError=1, searchWndName='stationMissionsSearchCharacterSearch')
        sm.GetService('loading').StopCycle()
        errMsg = mls.UI_MARKET_PLEASETYPEANDSEARCH
        scrolllist = []
        if charID:
            if type(charID) == types.TupleType:
                charID = int(charID[0])
            if type(charID) == types.IntType:
                charinfo = cfg.eveowners.Get(charID)
                self.placebountycharid = charID
                charMgr = sm.RemoteSvc('charMgr')
                staticinfo = charMgr.GetPublicInfo(charID)
                dynamicinfo = charMgr.GetPublicInfo3(charID)[0]
                balance = sm.GetService('wallet').GetWealth()
                scrolllist.append(listentry.Get('User', {'charID': charID,
                 'charinfo': charinfo,
                 'bounty': util.KeyVal(bounty=dynamicinfo.bounty)}))
                scrolllist.append(listentry.Get('Divider'))
                scrolllist.append(listentry.Get('Edit', {'OnReturn': None,
                 'label': mls.UI_GENERIC_BOUNTY,
                 'hint': mls.UI_STATION_TEXT35 % {'isk': util.FmtISK(5000)},
                 'setValue': 5000,
                 'name': 'bounty_amount',
                 'intmode': (5000, None)}))
                scrolllist.append(listentry.Get('Button', {'label': '',
                 'caption': mls.UI_CMD_ADDBOUNTY,
                 'OnClick': self.AddToBounty}))
                errMsg = None
            else:
                errMsg = charID
        else:
            scrolllist = []
        self.sr.scroll.Load(contentList=scrolllist, noContentHint=errMsg)
        sm.GetService('loading').StopCycle()



    def FindNode(self, nodeName):
        for entry in self.sr.scroll.GetNodes():
            if entry.name == nodeName:
                return entry




    def GetNodeValue(self, nodeName):
        node = self.FindNode(nodeName)
        if node is not None:
            return node.setValue
        raise RuntimeError('ChildNotFound', nodeName)



    def PlaceBountyExt(self, charID):
        if eve.session.stationid:
            blue.pyos.synchro.Yield()
            self.sr.tabs.ShowPanelByName(mls.UI_GENERIC_PLACEBOUNTY)
            self.SearchCharacter(charID)



    def AddToBounty(self, *args):
        charID = self.placebountycharid
        amount = self.GetNodeValue('bounty_amount')
        print charID,
        print amount
        if charID and amount:
            sm.RemoteSvc('charMgr').AddToBounty(charID, amount)
            self.placebountycharid = None
            self.SearchCharacter(charID)




