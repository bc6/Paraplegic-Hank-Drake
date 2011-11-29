import blue
import form
import listentry
import moniker
import sys
import uix
import uthread
import util
import xtriui
import uicls
import uiconst
import localization
import log
import fontConst
MILITIANEWSSURLS = {'optic': 'http://www.eve-online.com.cn/mb/fwnews.asp',
 'ccp': 'http://www.eveonline.com/mb/fwnews.asp'}

class MilitiaWindow(uicls.Window):
    __guid__ = 'form.MilitiaWindow'
    __notifyevents__ = ['OnJoinMilitia',
     'OnRankChange',
     'OnSessionChanged',
     'OnUIColorsChanged']
    default_width = 710
    default_height = 540
    default_windowID = 'militia'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.loading = 1
        self.bounties = None
        self.bountyCacheTimer = 0
        self.placebountycharid = None
        self.name = 'militia'
        self.infoCounter = None
        self.factionalWarStatus = None
        self.SetWndIcon('ui_61_128_3', size=128)
        self.SetMainIconSize(64)
        self.SetMinSize([710, 520])
        self.SetCaption(localization.GetByLabel('UI/Station/MilitiaOffice'))
        self.wCaption = uicls.WndCaptionLabel(text=' ', subcaption=' ', parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.sr.leftframe = uicls.Container(name='leftframe', align=uiconst.TOLEFT, parent=self.sr.main, width=512, top=0, clipChildren=1)
        uicls.Line(parent=self.sr.main, align=uiconst.TOLEFT)
        self.sr.rightframe = uicls.Container(name='rightframe', parent=self.sr.main, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), align=uiconst.TOALL)
        uicls.Container(name='push', parent=self.sr.rightframe, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        self.sr.buttonPar = uicls.Container(name='buttonParent', align=uiconst.TOBOTTOM, height=28, parent=self.sr.rightframe)
        self.browseScrollData = {}
        self.scrollGroupsLeftToLoad = ['militia', 'personal', 'corp']
        self.currentScrollGroups = []
        self.BuildData()
        if not self or self.destroyed:
            return 
        self.loading = 0
        self.Load()
        uthread.new(self.OpenNews, self.sr.rightframe, '%s?fwID=%s' % (MILITIANEWSSURLS.get(boot.region, ''), self.factionID))
        sm.RegisterNotify(self)



    def Load(self, key = None):
        if not self or self.destroyed:
            return 
        while self.loading:
            return 

        if key:
            if key in ('personal', 'corp', 'militia'):
                uthread.pool('MilitiaWindow::Load', self.Browse, key)
            return 
        wndHeight = 60
        uix.Flush(self.sr.leftframe)
        uicls.Line(parent=self.sr.leftframe, align=uiconst.TOTOP)
        self.sr.buttonPar.state = uiconst.UI_HIDDEN
        parallelCalls = []
        if not eve.session.warfactionid or eve.session.warfactionid != self.factionID:
            parallelCalls.append((self.LoadSignup, ()))
        else:
            parallelCalls.append((self.LoadFWInfo, ()))
        parallelCalls.append((self.LoadBackground, ()))
        self.sr.main.clipChildren = True
        uthread.parallel(parallelCalls)



    def OnSessionChanged(self, isRemote, session, change):
        if self and not self.destroyed:
            self.ReLoad()



    def OnUIColorsChanged(self, *args):
        (color, bgColor, comp, compsub,) = sm.GetService('window').GetWindowColors()
        if self and not self.destroyed:
            self.sr.fill.SetRGB(*comp)



    def OnJoinMilitia(self):
        if self and not self.destroyed:
            self.RefreshButtons()



    def OnRankChange(self, oldrank, newrank):
        if self and not self.destroyed:
            self.ReLoad()



    def ReLoad(self):
        if self.BuildData():
            uthread.new(self.Load)



    def BuildData(self):
        self.ShowLoad()
        self.factionID = sm.StartService('facwar').CheckStationElegibleForMilitia()
        if not self.factionID:
            self.Close()
            return False
        self.factionName = cfg.eveowners.Get(self.factionID).ownerName
        self.factionItem = cfg.eveowners.Get(self.factionID)
        self.militiaID = sm.StartService('facwar').GetFactionMilitiaCorporation(self.factionID)
        self.militiaItem = cfg.eveowners.Get(self.militiaID)
        self.militiaName = self.militiaItem.ownerName
        self.factionalWarStatus = sm.StartService('facwar').GetFactionalWarStatus()
        self.HideLoad()
        return True



    def GetFactionalCorporationString(self):
        factions = [ cfg.factions.Get(each) for each in sm.StartService('facwar').GetWarFactions() ]
        corporations = [ '&nbsp;<a href="showinfo:%s//%s">%s</a>,' % (const.typeCorporation, each.corporationID, cfg.eveowners.Get(each.corporationID).name) for each in factions ]
        corporations = ''.join(corporations)
        corporations = corporations[:-1]
        return corporations



    def OnEnlistMe(self, *args):
        sm.StartService('facwar').JoinFactionAsCharacter(self.factionID, eve.session.warfactionid)



    def OnEnlistMyCorp(self, *args):
        sm.StartService('facwar').JoinFactionAsCorporation(self.factionID, eve.session.warfactionid)



    def OpenNews(self, container, url, *args):
        browser = uicls.Edit(parent=container, readonly=1)
        browser.GoTo(url)



    def LoadBackground(self):
        if self and not self.destroyed and not self.sr.Get('bgsprite'):
            self.sr.bgsprite = uicls.Sprite(parent=self.sr.main, align=uiconst.RELATIVE, width=self.sr.leftframe.width, height=self.sr.leftframe.width, state=uiconst.UI_DISABLED)
            self.sr.bgsprite.color.a = 0.5
        self.sr.bgsprite.texture.resPath = 'res:/UI/Texture/Charsel/fw_%s_background.dds' % self.factionID



    def LoadSignup(self):
        wndHeight = 50
        self.wCaption.text = localization.GetByLabel('UI/FactionWarfare/JoinFactionWarfareHeader', factionName=self.factionName)
        textCont = uicls.Container(name='text', parent=self.sr.leftframe, align=uiconst.TOTOP, height=128, width=self.sr.leftframe.width)
        enlistInfoLabel = 'UI/Generic/Unknown'
        if self.factionID == 500001:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoCaldari'
        elif self.factionID == 500002:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoMinmatar'
        elif self.factionID == 500003:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoAmarr'
        elif self.factionID == 500004:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoGallente'
        else:
            log.LogError('Unknown Faction.')
        text = uicls.EveLabelMedium(text=localization.GetByLabel(enlistInfoLabel), parent=textCont, left=2 * const.defaultPadding, top=2 * const.defaultPadding, width=textCont.width - 4 * const.defaultPadding, state=uiconst.UI_NORMAL)
        textCont.height = text.height + const.defaultPadding
        wndHeight += textCont.height
        isSafe = sm.StartService('facwar').CheckForSafeSystem(eve.stationItem, self.factionID)
        warntxt = ''
        if not isSafe:
            warntxt = localization.GetByLabel('UI/FactionWarfare/CantEnlistHereInfo')
        hasReqRole = eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector
        if eve.session.warfactionid:
            infotxt = localization.GetByLabel('UI/FactionWarfare/AlreadyInAnotherFaction', factionName=self.factionName)
            buttons = []
        else:
            infotxt = localization.GetByLabel('UI/FactionWarfare/EnlistInfoForIndividual', factionName=self.factionName, militiaName=self.militiaName)
            buttons = [(80,
              110,
              localization.GetByLabel('UI/FactionWarfare/EnlistMe'),
              'enlistMe',
              self.factionName,
              self.OnEnlistMe,
              '72_16',
              -1,
              not isSafe)]
            if hasReqRole:
                self.wCaption.SetSubcaption(localization.GetByLabel('UI/FactionWarfare/SignupCorporationHint'))
                buttons.append((80,
                 110,
                 localization.GetByLabel('UI/FactionWarfare/EnlistCorporation'),
                 'enlistMyCorp',
                 self.factionName,
                 self.OnEnlistMyCorp,
                 '72_16',
                 -1,
                 False))
        uicls.Container(name='push', parent=self.sr.leftframe, align=uiconst.TOTOP, height=8)
        uix.GetContainerHeader(localization.GetByLabel('UI/Generic/Information'), self.sr.leftframe, 1)
        uicls.Container(name='push', parent=self.sr.leftframe, align=uiconst.TOTOP, height=4)
        wndHeight += 30
        buttonCont = uicls.Container(name='signupBtns', parent=self.sr.leftframe, align=uiconst.TORIGHT, width=98)
        buttonCont.state = uiconst.UI_HIDDEN if not buttons else uiconst.UI_NORMAL
        textCont = uicls.Container(name='text', parent=self.sr.leftframe, align=uiconst.TOALL, pos=(2 * const.defaultPadding,
         const.defaultPadding,
         2 * const.defaultPadding,
         const.defaultPadding))
        warnTextCont = None
        if warntxt:
            warnTextCont = uicls.Container(name='warntext', parent=textCont, align=uiconst.TOTOP, height=72)
            uicls.Container(name='push', parent=textCont, align=uiconst.TOTOP, height=4)
            uicls.Frame(parent=warnTextCont, color=(1.0, 1.0, 1.0, 0.125))
            uicls.Fill(parent=warnTextCont, color=(32 / 256.0,
             41 / 256.0,
             46 / 256.0,
             168 / 256.0))
            infoicon = uicls.Icon(parent=warnTextCont, icon='33_3', left=const.defaultPadding, top=const.defaultPadding, idx=0, width=64, height=64, state=uiconst.UI_DISABLED, ignoreSize=True)
            wrntext = uicls.EveHeaderSmall(text=warntxt, parent=warnTextCont, align=uiconst.TOALL, idx=0, top=8, left=72, width=6, state=uiconst.UI_NORMAL)
            warnTextCont.height = max(72, wrntext.textheight + 16)
        text = uicls.EveLabelMedium(text=infotxt, parent=textCont, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        btnHeight = 0
        for (i, (buttonSize, height, label, configname, desc, callback, iconPath, idx, isDisabled,),) in enumerate(buttons):
            btn = uix.GetBigButton(buttonSize, where=buttonCont, top=const.defaultPadding + (height * i + 22))
            btn.Click = callback
            btn.SetAlign(uiconst.BOTTOMLEFT)
            iconSize = 64
            y = x = buttonSize / 2 - iconSize / 2
            icon = uicls.Icon(parent=btn, left=x, top=y, idx=0, width=iconSize, height=iconSize, state=uiconst.UI_DISABLED, icon=iconPath, ignoreSize=True)
            btn.value = configname
            optionName = label
            btn.SetSmallCaption(optionName, maxWidth=100)
            btnHeight += height + 26
            if isDisabled:
                ALPHA = 0.35
                icon.color.a = ALPHA
                btn.state = uiconst.UI_DISABLED
                btn.sr.smallcaption.color.a = ALPHA

        wndHeight += max(btnHeight, (0 if not warnTextCont else warnTextCont.height) + text.textheight + 32)
        self.SetHeight(wndHeight)
        self.SetMinSize([710, wndHeight])
        self.sr.buttonPar.Flush()
        self.sr.buttonPar.state = uiconst.UI_HIDDEN
        if util.IsNPC(session.corpid):
            rightBtn = []
            if eve.session.warfactionid:
                rightBtn.append((localization.GetByLabel('UI/FactionWarfare/Retire'),
                 self.Retire,
                 (),
                 84))
                buttonWnd = uicls.ButtonGroup(btns=rightBtn, parent=self.sr.buttonPar, unisize=1, line=0)
                self.sr.buttonPar.state = uiconst.UI_NORMAL
            else:
                return 
        else:
            fwStatus = self.factionalWarStatus.status
            if fwStatus == None:
                return 
            if hasReqRole:
                self.RefreshButtons()
            else:
                return 



    def LoadFWInfo(self):
        buttons = []
        if eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            fwStatus = self.factionalWarStatus.status
            pendingFactionID = self.factionalWarStatus.factionID
            if fwStatus == const.facwarCorporationLeaving:
                buttons.append((localization.GetByLabel('UI/FactionWarfare/CancelRetirement'),
                 self.CancelRetirement,
                 pendingFactionID,
                 84))
            elif fwStatus == const.facwarCorporationActive:
                buttons.append((localization.GetByLabel('UI/FactionWarfare/RetireCorporation'),
                 self.RetireCorp,
                 pendingFactionID,
                 84))
        elif util.IsNPC(session.corpid):
            buttons.append((localization.GetByLabel('UI/FactionWarfare/Retire'),
             self.Retire,
             (),
             84))
        if buttons:
            self.sr.buttonPar.state = uiconst.UI_PICKCHILDREN
            self.sr.buttonPar.Flush()
            buttonWnd = uicls.ButtonGroup(btns=buttons, parent=self.sr.buttonPar, unisize=1, line=0)
        self.wCaption.text = localization.GetByLabel('UI/FactionWarfare/BattlefieldIntelligence')
        uix.GetContainerHeader(localization.GetByLabel('UI/Generic/Information'), self.sr.leftframe, 0)
        enemies = sm.StartService('facwar').GetEnemies(self.factionID)
        if len(enemies) != 2:
            log.LogError('Expecting only two factions at war with any given faction, not more than that')
        self.wCaption.SetSubcaption(localization.GetByLabel('UI/FactionWarfare/AtWarWith', factionName1=cfg.eveowners.Get(enemies[0]).name, factionName2=cfg.eveowners.Get(enemies[1]).name))
        rankPar = uicls.Container(name='rankPar', parent=self.sr.leftframe, align=uiconst.TOTOP, width=self.sr.leftframe.width, height=100)
        theLeft = 0
        logo = uicls.LogoIcon(itemID=self.factionID, parent=rankPar, left=const.defaultPadding * 2, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, size=85, ignoreSize=True)
        theLeft += logo.width
        faction_infoicon = uicls.InfoIcon(typeID=const.typeFaction, itemID=self.factionID, size=16, left=logo.left + logo.width - 16, top=const.defaultPadding * 2, parent=rankPar, idx=0, align=uiconst.TOPLEFT)
        rankCont = uicls.Container(name='rank', parent=rankPar, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        currRank = sm.StartService('facwar').GetCharacterRankInfo(session.charid) or util.KeyVal(currentRank=1, highestRank=1, factionID=self.factionID)
        if currRank:
            currentRank = currRank.currentRank
            rank = xtriui.Rank(parent=rankCont, align=uiconst.TOPRIGHT, width=84, height=84)
            rank.Startup(self.factionID, currentRank)
            rank.SetAlign(uiconst.CENTERRIGHT)
            rank.left = const.defaultPadding * 2
            try:
                timeInFW = blue.os.GetWallclockTime() - max(self.factionalWarStatus.startDate, sm.RemoteSvc('corporationSvc').GetEmploymentRecord(session.charid)[0].startDate)
                timeInFW = util.FmtTimeInterval(timeInFW, 'day')
            except:
                timeInFW = localization.GetByLabel('UI/Generic/Unknown')
            (rankName, rankDescription,) = sm.GetService('facwar').GetRankLabel(self.factionID, currentRank)
            txt = localization.GetByLabel('UI/FactionWarfare/FactionAndCorporation', militiaItem=self.factionItem.name, corporationItem=cfg.eveowners.Get(session.corpid).name, rankName=rankName, militiaDuration=timeInFW)
            self.sr.fill = uicls.Fill(parent=rankCont, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            uicls.Frame(parent=rankCont, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            rankText = uicls.EveLabelMedium(text=txt, parent=rankCont, state=uiconst.UI_DISABLED, tabs=[120, 340], idx=0, align=uiconst.CENTER)
            abstractinfo = util.KeyVal(warFactionID=self.factionID, currentRank=currentRank)
            rank_infoicon = uicls.InfoIcon(typeID=const.typeRank, size=16, left=const.defaultPadding * 2, top=const.defaultPadding * 2, parent=rankCont, idx=0, abstractinfo=abstractinfo, align=uiconst.TOPRIGHT)
        systemStatsCont = uicls.Container(name='systemStatsCont', parent=self.sr.leftframe, align=uiconst.TOBOTTOM, height=160)
        uix.GetContainerHeader(localization.GetByLabel('UI/Agents/AdditionalInformation'), systemStatsCont)
        uicls.Container(name='push', parent=systemStatsCont, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        statsGroups = [('statsLeft',
          systemStatsCont,
          uiconst.TOLEFT,
          self.sr.leftframe.width / 3,
          'nearby'), ('statsRight',
          systemStatsCont,
          uiconst.TORIGHT,
          self.sr.leftframe.width / 3,
          'conquered'), ('statsCenter',
          systemStatsCont,
          uiconst.TOALL,
          0,
          'dangerous')]
        maxScrollHeight = 0
        for (configname, where, align, width, index,) in statsGroups:
            statsGroupParent = uicls.Container(name='%sParent' % configname, parent=where, align=align, width=width)
            if configname == 'push':
                continue
            headerCont = uicls.Container(name='%sHeaderCont' % configname, parent=statsGroupParent, align=uiconst.TOTOP, width=width, height=18)
            header = uicls.EveHeaderMedium(text=' ', parent=headerCont, left=const.defaultPadding, top=2, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
            setattr(self.sr, '%sHeader' % configname, header)
            p = const.defaultPadding
            scroll = uicls.Scroll(name='configname', parent=statsGroupParent, padding=(p,
             p,
             p,
             p))
            scroll.sr.activeframe = None
            self.FormatScroll(scroll)
            self.SetStaticScroll(index, scroll, configname)
            maxScrollHeight = scroll.height
            setattr(self, configname, scroll)

        uix.GetContainerHeader(localization.GetByLabel('UI/Generic/Statistics'), self.sr.leftframe)
        self.sr.infoCont = uicls.Container(name='info', parent=self.sr.leftframe, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        panel = uicls.Container(name='panel', parent=self.sr.infoCont, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        self.sr.panel = panel
        self.sr.maintabs = uicls.TabGroup(name='tabparent', parent=self.sr.infoCont, idx=0)
        maintabs = [[localization.GetByLabel('UI/FactionWarfare/Militia'),
          None,
          self,
          'militia'], [localization.GetByLabel('UI/Generic/Personal'),
          None,
          self,
          'personal'], [localization.GetByLabel('UI/Generic/Corporation'),
          None,
          self,
          'corp']]
        self.sr.maintabs.Startup(maintabs, 'militiainformationtabs', autoselecttab=0)
        self.sr.maintabs.AutoSelect()
        self.sr.infoScroll = uicls.Scroll(parent=self.sr.panel)
        self.OnUIColorsChanged()
        self.FormatScroll(self.sr.infoScroll)
        self.SetHeight(520)
        self.SetMinSize([710, 520])



    def RetireCorp(self, factionID, *args):
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            sm.StartService('facwar').LeaveFactionAsCorporation(factionID)
            self.RefreshButtons()



    def Retire(self, *args):
        factionID = session.warfactionid
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            corp = sm.StartService('corp')
            corp.KickOut(session.charid, confirm=False)
            sm.StartService('objectCaching').InvalidateCachedMethodCall('corporationSvc', 'GetEmploymentRecord', session.charid)



    def CopyTable(self, *args):
        menu = [(localization.GetByLabel('UI/FactionWarfare/CopyTable'), self.CopyScroll, (self.sr.infoScroll,))]
        return menu



    def CopyScroll(self, scroll, *args):
        t = ''
        if hasattr(scroll, 'sr') and hasattr(scroll.sr, 'headers'):
            for header in getattr(scroll.sr, 'headers', None):
                if header == '':
                    header = '-'
                t = t + '%s, ' % header

        for each in scroll.GetNodes():
            t = t + '\r\n%s' % each.label.replace('<t>', ',  ').replace('<b>', '').replace('</b>', '')

        blue.pyos.SetClipboardData(t)



    def CancelApplication(self, factionID):
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelApplicationHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelApplication', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            sm.StartService('facwar').WithdrawJoinFactionAsCorporation(factionID)
            self.RefreshButtons()



    def CancelRetirement(self, factionID):
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelRetirementHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelRetirementHeader', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            sm.StartService('facwar').WithdrawLeaveFactionAsCorporation(factionID)
            self.RefreshButtons()



    def RefreshButtons(self):
        self.factionalWarStatus = sm.StartService('facwar').GetFactionalWarStatus()
        fwStatus = self.factionalWarStatus.status
        pendingFactionID = self.factionalWarStatus.factionID
        self.sr.buttonPar.Flush()
        self.sr.buttonPar.state = uiconst.UI_HIDDEN
        rightBtn = []
        if fwStatus == const.facwarCorporationJoining:
            rightBtn.append((localization.GetByLabel('UI/FactionWarfare/WithdrawApplication'),
             self.CancelApplication,
             pendingFactionID,
             84))
        elif fwStatus == const.facwarCorporationActive:
            rightBtn.append((localization.GetByLabel('UI/FactionWarfare/RetireCorporation'),
             self.RetireCorp,
             pendingFactionID,
             84))
        elif fwStatus == const.facwarCorporationLeaving:
            rightBtn.append((localization.GetByLabel('UI/FactionWarfare/CancelRetirement'),
             self.CancelRetirement,
             pendingFactionID,
             84))
        else:
            return 
        buttonWnd = uicls.ButtonGroup(btns=rightBtn, parent=self.sr.buttonPar, unisize=1, line=0)
        self.sr.buttonPar.state = uiconst.UI_NORMAL



    def FormatScroll(self, scroll):
        pass



    def SetStaticScroll(self, statsType, cont, victimString):
        scrolllist = []
        scrolllist = self.GetStaticScrollList(statsType, victimString)
        scrolllist = scrolllist[:min(len(scrolllist), 6)]
        cont.Load(contentList=scrolllist, headers=[])
        if len(scrolllist) == 0:
            cont.ShowHint(localization.GetByLabel('UI/Generic/NoDataAvailable'))
        cont.sr.scrollHeaders.state = uiconst.UI_HIDDEN



    def Browse(self, key = None):
        self.SetBrowseScroll(key)



    def SetBrowseScroll(self, key):
        self.LoadScrollGroup(key)
        (scrolllist, header,) = self.BrowseScrollContent(key, self.browseScrollData)
        self.sr.infoScroll.Load(contentList=scrolllist, headers=header)



    def BrowseScrollContent(self, key, browseScrollData, *args):
        stats = browseScrollData[key]
        caption = stats.get('label', '')
        header = stats.get('header', [])
        list = stats.get('data', [])
        scrolllist = []
        for each in list:
            data = util.KeyVal()
            data.label = each
            data.vspace = 0
            data.GetMenu = self.CopyTable
            data.selectable = 0
            scrolllist.append(listentry.Get('Generic', data=data))

        return (scrolllist, header)



    def LoadScrollGroup(self, key):
        stats = self.GetStatsData(key)
        if not stats:
            return 
        statsHeader = stats.get('header')
        statsData = stats.get('data')
        data = [self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/KillsYesterday'), statsHeader, statsData.get('killsY')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/KillsLastWeek'), statsHeader, statsData.get('killsLW')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/KillsTotal'), statsHeader, statsData.get('killsTotal')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/VictoryPointsYesterday'), statsHeader, statsData.get('vpY')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/VictoryPointsLastWeek'), statsHeader, statsData.get('vpLW')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/VictoryPointsTotal'), statsHeader, statsData.get('vpTotal'))]
        factionInfo = sm.StartService('facwar').GetStats_FactionInfo()
        if key == 'militia':
            memberCount = self.ChangeFormat(factionInfo, 'totalMembersCount')
            sysControlled = self.ChangeFormat(factionInfo, 'systemsCount')
            data.insert(0, self.GetLine(localization.GetByLabel('UI/FactionWarfare/Pilots'), statsHeader, memberCount))
            data.append(self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/SystemsControlled'), statsHeader, sysControlled))
        if key == 'corp':
            corpPilots = self.GetCorpPilots(factionInfo)
            data.insert(0, self.GetLine(localization.GetByLabel('UI/FactionWarfare/Pilots'), statsHeader, corpPilots))
        self.browseScrollData[key] = {'label': self.GetStatsLabel(key),
         'configname': key,
         'header': self.GetStatsHeader(key, statsHeader),
         'data': data}
        self.currentScrollGroups.append(key)



    def GetCorpPilots(self, factionInfo):
        pilots = {}
        if util.IsNPC(session.corpid):
            yourFactionInfo = factionInfo.get(eve.session.warfactionid, None)
            pilots['your'] = getattr(yourFactionInfo, 'militiaMembersCount', 0)
        else:
            reg = moniker.GetCorpRegistry()
            pilots['your'] = reg.GetCorporation().memberCount
        topFWCorp = 0
        topCorps = self.ChangeFormat(factionInfo, 'topMemberCount')
        for each in topCorps.itervalues():
            if topFWCorp < each:
                topFWCorp = each

        pilots['top'] = topFWCorp
        allMembers = 0
        members = self.ChangeFormat(factionInfo, 'totalMembersCount')
        for each in members.itervalues():
            allMembers += each

        pilots['all'] = allMembers
        return pilots



    def ChangeFormat(self, data, attributeName):
        temp = {}
        for (key, value,) in data.iteritems():
            temp[key] = getattr(value, attributeName, 0)

        return temp



    def GetStatsData(self, what):
        if what == 'militia':
            return sm.StartService('facwar').GetStats_Militia()
        if what == 'personal':
            return sm.StartService('facwar').GetStats_Personal()
        if what == 'corp':
            return sm.StartService('facwar').GetStats_Corp(session.corpid)



    def GetStatsLabel(self, what):
        if what == 'militia':
            return localization.GetByLabel('UI/FactionWarfare/Militia')
        if what == 'personal':
            return localization.GetByLabel('UI/Generic/Personal')
        if what == 'corp':
            return localization.GetByLabel('UI/Generic/Corporation')
        return ''



    def GetStatsHeader(self, what, header):
        if what in ('personal', 'corp'):
            return self.GetPersonalCorpHeader(header)
        if what == 'militia':
            return self.GetMilitiaHeader(header, short=1)
        return []



    def GetLine(self, text, header, data):
        temp = '%s<t>' % text
        for each in header:
            temp = '%s%s<t>' % (temp, util.FmtAmt(data.get(each, 0), fmt='sn'))

        temp = temp[:-3]
        return temp



    def GetMilitiaHeader(self, header, short = 0):
        temp = [localization.GetByLabel('UI/Generic/Statistics')]
        for each in header:
            name = cfg.eveowners.Get(each).name
            if short:
                name = name[0:name.find(' ')] if name.find(' ') != -1 else name
            temp.append(name)

        return temp



    def GetPersonalCorpHeader(self, header):
        translation = {'you': localization.GetByLabel('UI/FactionWarfare/You'),
         'your': localization.GetByLabel('UI/FactionWarfare/Your'),
         'top': localization.GetByLabel('UI/FactionWarfare/Top'),
         'all': localization.GetByLabel('UI/FactionWarfare/All')}
        temp = [localization.GetByLabel('UI/Generic/Statistics')]
        for each in header:
            name = translation.get(each, '')
            temp.append(name)

        return temp



    def GetStaticScrollList(self, statsType, victimString):
        text = self.sr.Get('%sHeader' % victimString, None)
        headerInfo = self.GetHeaderAndHint(statsType)
        text.text = localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=headerInfo.header)
        text.hint = headerInfo.hint
        statlist = self.GetList(statsType)
        scrolllist = []
        for each in statlist:
            data = util.KeyVal()
            data.label = self.GetLabel(statsType, each)
            data.itemID = self.GetSolarsystemID(each)
            data.typeID = 5
            data.fontsize = fontConst.EVE_MEDIUM_FONTSIZE
            data.selectable = 0
            data.showinfo = 1
            data.hint = self.GetSystemHint(statsType, each)
            scrolllist.append(listentry.Get('Generic', data=data))

        return scrolllist



    def GetHeaderAndHint(self, statsType):
        headerInfo = util.KeyVal(header='', hint='')
        if statsType == 'nearby':
            headerInfo.header = localization.GetByLabel('UI/FactionWarfare/Stats/NearbySystems')
            headerInfo.hint = localization.GetByLabel('UI/FactionWarfare/Stats/NearbySystemsHeaderHint')
        elif statsType == 'dangerous':
            headerInfo.header = localization.GetByLabel('UI/FactionWarfare/Stats/DangerousSystems')
            headerInfo.hint = localization.GetByLabel('UI/FactionWarfare/Stats/DangerousSystemsHeaderHint')
        elif statsType == 'conquered':
            headerInfo.header = localization.GetByLabel('UI/FactionWarfare/Stats/ConqueredSystems')
            headerInfo.hint = localization.GetByLabel('UI/FactionWarfare/Stats/ConqueredSystemsHeaderHint')
        return headerInfo



    def GetList(self, statsType):
        if statsType == 'nearby':
            return sm.StartService('facwar').GetDistanceToEnemySystems() or []
        if statsType == 'dangerous':
            return sm.StartService('facwar').GetMostDangerousSystems() or []
        if statsType == 'conquered':
            return sm.StartService('facwar').GetStats_Systems() or []
        return []



    def GetLabel(self, statsType, each):
        label = cfg.evelocations.Get(each.solarSystemID).name if isinstance(each, util.KeyVal) else cfg.evelocations.Get(each.get('solarsystemID', 0)).name
        return label



    def GetSolarsystemID(self, each):
        itemID = each.solarSystemID if isinstance(each, util.KeyVal) else cfg.evelocations.Get(each.get('solarsystemID', 0)).locationID
        return itemID



    def GetSystemHint(self, statsType, each):
        if statsType == 'nearby':
            hint = localization.GetByLabel('UI/FactionWarfare/Stats/NearbySystemsHint', occupierName=cfg.eveowners.Get(each.occupierID).name, jumps=each.numJumps)
            return hint
        if statsType == 'dangerous':
            hint = localization.GetByLabel('UI/FactionWarfare/Stats/DangerousSystemsHint', kills=each.numKills)
            return hint
        if statsType == 'conquered':
            hint = localization.GetByLabel('UI/FactionWarfare/Stats/ConqueredSystemsHint', factionName=cfg.eveowners.Get(each.get('occupierID', 0)).name, time=each.get('taken', 0L))
            return hint
        return ''




