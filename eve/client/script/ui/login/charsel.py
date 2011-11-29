import trinity
import uix
import uiutil
import blue
import uthread
import util
import xtriui
import random
import log
import base
import service
import uicls
import uiconst
import ccUtil
import localization
import localizationUtil
import fontConst

class CharSelection(uicls.LayerCore):
    __guid__ = 'form.CharSelection'
    __nonpersistvars__ = ['ready',
     'selected',
     'freeslots',
     'wnd',
     'activeframe']
    __notifyevents__ = ['OnSetDevice',
     'OnJumpQueueMessage',
     'OnCharacterHandler',
     'OnUIRefresh']

    def OnSetDevice(self):
        if not self.isopen or self.wnd is None or self.wnd.destroyed:
            return 
        for slot in self.sr.slots:
            slot.Close()

        self.sr.slots = []
        borderHeight = uicore.desktop.height / 6
        bottomHeight = 115
        browserWidth = int(uicore.desktop.width * 0.33)
        smallPush = 20
        leftPush = 42
        self.sr.par.height = borderHeight
        self.sr.browser.width = browserWidth
        charContHeight = uicore.desktop.height - borderHeight - bottomHeight - smallPush
        charContWidth = uicore.desktop.width - browserWidth - smallPush - leftPush - 2
        size = charContHeight / 2
        self.size = int(min(size, charContWidth * 0.5, 400))
        self.sr.buttonCont.width = self.size
        centerContWidth = charContWidth - self.size - 3 * smallPush
        self.infoWidth = max(325, min(centerContWidth, 450, int(0.35 * uicore.desktop.width)))
        self.sr.infoParent.width = self.infoWidth
        self.sr.infoParent.height = charContHeight
        self.fontSize = fontConst.EVE_SMALL_FONTSIZE
        if self.infoWidth > 400:
            self.fontSize = fontConst.EVE_MEDIUM_FONTSIZE
        uthread.new(self.SetupSlots, True)



    def OnUIRefresh(self):
        self.CloseView(recreate=False)
        self.OpenView()



    def OnCloseView(self):
        w = self.wnd
        self.wnd = None
        if w is not None and not w.destroyed:
            w.Close()



    def OnJumpQueueMessage(self, msgtext, ready):
        if not (self.sr.Get('slot0') and hasattr(self.sr.slot0, 'sr') and self.sr.slot0.sr.charid):
            log.LogInfo('Jump Queue:  The UI is in a funky state, no slam-thru')
            return 
        if not (self.sr.slot0 and self.sr.slot0.sr.charid and self.sr.slot0.sr.charid == sm.GetService('jumpQueue').GetPreparedQueueCharID()):
            log.LogInfo("Jump Queue:  The prepared character isn't the right one.  Not slamming through char selection")
            return 
        if ready:
            log.LogInfo('Jump Queue: ready, slamming through...')
            self._CharSelection__Confirm(sm.GetService('jumpQueue').GetPreparedQueueCharID())
        else:
            log.LogInfo('Jump Queue: message=', msgtext)
            self._CharSelection__Say(msgtext)



    def __Say(self, msgtext):
        if not trinity.device:
            log.LogError("Returning because we don't have a device :(")
            return 
        for each in uicore.layer.main.children:
            if each.name == 'message':
                if msgtext:
                    each.ShowMsg(msgtext)
                else:
                    each.hide()
                return 

        if msgtext:
            uicore.Say(msgtext)
            log.LogInfo('Jump Queue:  On Jump Queue Message displayed')



    def GetChars(self, reload = 0):
        return sm.GetService('cc').GetCharactersToSelect(reload)



    def OnOpenView(self):
        self.sr.slots = []
        self.details = {}
        self.wnd = None
        self.opened = 0
        self.countDownTimer = None
        self.totds = []
        self.isTabStop = 1
        bgMusic = sm.StartService('jukebox').GetState()
        if bgMusic == 'pause':
            sm.StartService('jukebox').Play()
        if not sm.GetService('connection').IsConnected():
            return 
        self.chars = self.GetChars(reload=True)
        self.redeemTokens = sm.StartService('redeem').GetRedeemTokens()
        if len(self.chars) > 3:
            log.LogWarn('There are more than 3 characters')
            self.chars = self.chars[:3]
        self.wnd = uicls.Container(name='charsel', parent=self, state=uiconst.UI_PICKCHILDREN)
        self.InitScene()
        self.InitUI()
        sm.StartService('lightFx')
        self.opened = 1



    def InitUI(self):
        if self.wnd is None or self.wnd.destroyed:
            return 
        self.buttonSize = 64
        for slot in self.sr.slots:
            slot.Close()

        self.sr.slots = []
        self.sr.main = None
        self.wnd.Flush()
        borderHeight = uicore.desktop.height / 6
        bottomHeight = 115
        browserWidth = int(uicore.desktop.width * 0.33)
        smallPush = 20
        leftPush = 42
        self.sr.par = uicls.Container(name='underlayContainer', parent=self.wnd, align=uiconst.TOTOP, height=borderHeight)
        banner = uicls.Container(name='topCont', parent=self.sr.par, align=uiconst.TOALL, padTop=40)
        caption = uicls.EveCaptionLarge(text='', parent=banner, align=uiconst.BOTTOMLEFT, top=8, left=40)
        uicls.Sprite(parent=banner, align=uiconst.CENTER, width=168, height=64, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/EVE_logo_cc.dds')
        uicls.Line(parent=banner, align=uiconst.TOTOP, weight=1)
        uicls.Line(parent=banner, align=uiconst.TOBOTTOM, weight=1)
        uicls.Fill(parent=banner, color=(0.2, 0.2, 0.2, 0.4))
        self.sr.main = uicls.Container(name='main', parent=self.wnd, align=uiconst.TOALL)
        self.sr.browser = uicls.Edit(parent=self.sr.main, readonly=1, hideBackground=1, padBottom=20, padLeft=2, padTop=smallPush, align=uiconst.TORIGHT, width=browserWidth, name='browser')
        uicls.Fill(parent=self.sr.browser, color=(0.2, 0.2, 0.2, 0.4))
        self.sr.browser.sr.activeframe.color.a = 0.0
        uicls.Fill(parent=self.sr.browser.sr.scrollcontrols, color=(0.0, 0.0, 0.0, 1.0))
        uthread.new(self.OpenNews, self.sr.browser)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=smallPush)
        uicls.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=leftPush)
        bottompane = uicls.Container(name='bottompane', parent=self.sr.main, align=uiconst.TOBOTTOM, height=bottomHeight)
        self.sr.bottomBtnCont = uicls.Container(name='bottomBtnCont', parent=bottompane, align=uiconst.TORIGHT, width=150)
        self.sr.totdCont = uicls.Container(name='totdCont', parent=bottompane, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        charCont = uicls.Container(name='charCont', parent=self.sr.main, padTop=20)
        charContHeight = uicore.desktop.height - borderHeight - bottomHeight - smallPush
        charContWidth = uicore.desktop.width - browserWidth - smallPush - leftPush - 2
        size = charContHeight / 2
        self.size = int(min(size, charContWidth * 0.5, 400))
        self.sr.buttonCont = uicls.Container(name='buttonCont', parent=charCont, align=uiconst.TOLEFT, width=self.size)
        uicls.Container(name='push', parent=charCont, align=uiconst.TOLEFT, width=smallPush)
        self.sr.centerCont = uicls.Container(name='centerCont', parent=charCont)
        centerContWidth = charContWidth - self.size - 3 * smallPush
        self.infoWidth = max(325, min(centerContWidth, 450, int(0.35 * uicore.desktop.width)))
        self.sr.infoParent = uicls.Container(name='infoParent', parent=self.sr.centerCont, align=uiconst.CENTERTOP, width=self.infoWidth, height=charContHeight)
        self.sr.infoButtonCont = uicls.Container(name='infoButtonCont', parent=self.sr.infoParent, align=uiconst.TOBOTTOM, height=24)
        self.sr.editControl = uicls.Edit(parent=self.sr.infoParent, readonly=1, hideBackground=1, showattributepanel=0)
        self.sr.editControl.scrollEnabled = 0
        self.fontSize = fontConst.EVE_SMALL_FONTSIZE
        self.letterspace = 0
        if self.infoWidth > 400:
            self.fontSize = fontConst.EVE_MEDIUM_FONTSIZE
        if len(self.chars) == 3:
            caption.text = localization.GetByLabel('UI/CharacterSelection/SelectCharacter')
        elif 0 < len(self.chars) < 3:
            caption.text = localization.GetByLabel('UI/CharacterSelection/SelectOrCreateCharacter')
        else:
            caption.text = ''
        uthread.new(self.SetupSlots)



    def OnCharacterHandler(self):
        uthread.new(self.LoadCharacters, True, True)



    def SetupSlots(self, reload = False):
        log.LogInfo('Character selection: Setting up the slots')
        self.ready = 0
        slotsPar = uicls.Container(name='slotsPar', parent=self.sr.buttonCont, pos=(0, 0, 0, 0))
        (l, t, w, h,) = slotsPar.GetAbsolute()
        size = self.size
        self.sr.subparent = uicls.Container(name='subparent', parent=slotsPar, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        space = 36
        small = (size - space) / 2
        slots = [(0,
          size,
          0,
          0), (1,
          small,
          0,
          size + space), (2,
          small,
          small + space,
          size + space)]
        self.SetupButtons()
        for (i, buttonSize, X, Y,) in slots:
            btn = xtriui.BigButton(parent=self.sr.subparent, left=X, top=Y, width=buttonSize, height=buttonSize, idx=0)
            btn.Startup(buttonSize, buttonSize)
            btn.GetMenu = (self.GetSlotMenu, btn)
            btn.OnClick = (self.SelectSlot, btn)
            btn.OnDblClick = (self.SelectSlot, btn)
            btn.sr.charid = None
            btn.sr.time = None
            btn.sr.rec = None
            btn.sr.idx = i
            self.sr.slots.append(btn)
            setattr(self.sr, 'slot%s' % i, btn)
            delete = uix.GetBigButton(32, btn, btn.width - 32 - 6, btn.height - 32 - 6)
            delete.OnClick = self.Terminate
            delete.sr.hint = localization.GetByLabel('UI/CharacterSelection/Terminate')
            delete.sr.icon.LoadIcon('4_16')
            uiutil.SetOrder(delete, 0)
            btn.sr.delete = delete
            btn.sr.delete.state = uiconst.UI_HIDDEN
            if i == 0:
                btn.sr.activity = uicls.Container(name='activity', parent=btn, align=uiconst.TOPLEFT, left=8, top=12, width=42, height=48, state=uiconst.UI_HIDDEN, idx=0)
                fillColor = (0.6, 0.6, 0.6, 0.35)
                color = (0.93, 0.79, 0.0, 0.65)
                btn.sr.calendar = uicls.Container(name='calendar', parent=btn.sr.activity, align=uiconst.TOTOP, width=42, height=24, state=uiconst.UI_HIDDEN, idx=0)
                uicls.Fill(parent=btn.sr.calendar, color=fillColor)
                self.sr.calendarIcon = uicls.Icon(icon='ui_73_16_40', parent=btn.sr.calendar, pos=(4, 4, 16, 16), align=uiconst.TOPLEFT, idx=0)
                self.sr.calendarIcon.color.SetRGB(*color)
                btn.sr.calendarText = uicls.Label(text='', parent=btn.sr.calendar, color=color, idx=0, fontsize=13, left=24, top=4, state=uiconst.UI_NORMAL)
                btn.sr.mail = uicls.Container(name='mail', parent=btn.sr.activity, align=uiconst.TOTOP, width=42, height=24, state=uiconst.UI_HIDDEN, idx=0)
                uicls.Fill(parent=btn.sr.mail, color=fillColor)
                self.sr.mailIcon = uicls.Icon(icon='ui_73_16_41', parent=btn.sr.mail, pos=(4, 4, 16, 16), align=uiconst.TOPLEFT, idx=0)
                self.sr.mailIcon.color.SetRGB(*color)
                btn.sr.mailText = uicls.Label(text='', parent=btn.sr.mail, color=color, idx=0, fontsize=13, left=24, top=4, state=uiconst.UI_NORMAL)

        self.LoadCharacters()
        if not reload:
            self.LoadTOTD()
            uicore.registry.SetFocus(self.sr.enterBtn)
        sm.ScatterEvent('OnClientReady', 'charsLoaded')



    def LoadTOTD(self, direction = 0, *args):
        currlabel = self.sr.tipofthedayText.text
        label = ''
        currentLabel = self.sr.tipofthedayText.text.replace(label, '')
        currentIndex = 0
        if not self.totds:
            allFound = False
            i = 1
            while not allFound:
                labelPath = 'UI/CharacterSelection/TipOfTheDay/Tip%s' % i
                if localization.IsValidLabel(labelPath):
                    self.totds.append(localization.GetByLabel(labelPath))
                    i += 1
                else:
                    allFound = True

        if len(self.totds):
            self.sr.totdCont.Show()
            if currentLabel in self.totds:
                currentIndex = self.totds.index(currentLabel)
            if direction == 0:
                currentIndex = random.randint(0, len(self.totds) - 1)
                label = self.totds[currentIndex]
            elif direction == -1:
                currentIndex = max(0, currentIndex - 1)
            elif direction == 1:
                currentIndex = min(len(self.totds) - 1, currentIndex + 1)
            label = self.totds[currentIndex]
            if currentIndex == len(self.totds) - 1:
                self.sr.nextTOTDBtn.state = uiconst.UI_DISABLED
                self.sr.nextTOTDBtn.hint = ''
            else:
                self.sr.nextTOTDBtn.state = uiconst.UI_NORMAL
                self.sr.nextTOTDBtn.hint = localization.GetByLabel('UI/CharacterSelection/NextTip')
            if currentIndex == 0:
                self.sr.prevTOTDBtn.state = uiconst.UI_DISABLED
                self.sr.prevTOTDBtn.hint = ''
            else:
                self.sr.prevTOTDBtn.state = uiconst.UI_NORMAL
                self.sr.prevTOTDBtn.hint = localization.GetByLabel('UI/CharacterSelection/PreviousTip')
            self.sr.nextTOTDBtn.color.a = 0.3 if currentIndex == len(self.totds) - 1 else 1.0
            self.sr.prevTOTDBtn.color.a = 0.3 if currentIndex == 0 else 1.0
        else:
            self.sr.totdCont.Hide()
        self.sr.tipofthedayText.text = label



    def SetupButtons(self):
        btns = [(localization.GetByLabel('UI/CharacterSelection/EnterGame'),
          'ui_23_64_2',
          'enter',
          self.Confirm,
          0), (localization.GetByLabel('UI/CharacterSelection/RedeemItems'),
          'ui_76_64_3',
          'redeem',
          self.Redeem,
          80)]
        totdbtns = [(localization.GetByLabel('UI/CharacterSelection/PreviousTip'),
          'ui_23_64_1',
          'prevTOTD',
          self.LoadTOTD,
          -1,
          0), (localization.GetByLabel('UI/CharacterSelection/RandomTip'),
          'ui_23_64_3',
          'randomTOTD',
          self.LoadTOTD,
          0,
          1), (localization.GetByLabel('UI/CharacterSelection/NextTip'),
          'ui_23_64_2',
          'nextTOTD',
          self.LoadTOTD,
          1,
          0)]
        top = 40
        self.sr.tipofthedayCaption = uicls.Label(text=localization.GetByLabel('UI/CharacterSelection/TipOfTheDay'), parent=self.sr.totdCont, fontsize=self.fontSize + 3, top=top, left=20, color=None, state=uiconst.UI_NORMAL, idx=0)
        self.sr.tipofthedayText = uicls.Label(text='', parent=self.sr.totdCont, align=uiconst.TOALL, fontsize=self.fontSize + 3, top=self.sr.tipofthedayCaption.top + self.sr.tipofthedayCaption.textheight, left=20, color=None, state=uiconst.UI_NORMAL, idx=0)
        for (caption, icon, button, func, offset,) in btns:
            btn = getattr(self.sr, '%sBtn' % button, None)
            if btn:
                btn.Close()
            btn = uix.GetBigButton(64, self.sr.bottomBtnCont)
            btn.SetSmallCaption(caption, maxWidth=64)
            btn.SetAlign(align=uiconst.TOPRIGHT)
            btn.left = offset
            btn.hint = caption
            btn.Click = func
            btn.sr.icon.LoadIcon(icon)
            btn.name = '%sBtn' % button
            uiutil.SetOrder(btn, 0)
            setattr(self.sr, '%sBtn' % button, btn)
            btn.state = uiconst.UI_HIDDEN
            if button == 'enter':
                btn.btn_default = 1

        for (caption, icon, button, func, direction, y,) in totdbtns:
            btn = getattr(self.sr, '%sBtn' % button, None)
            if btn:
                btn.Close()
            btn = uicls.Icon(icon='ui_73_16_%s' % (direction + 3), pos=(0,
             top + y * 16 - 2,
             0,
             0), hint=caption, name='%sBtn' % button, parent=self.sr.totdCont, align=uiconst.RELATIVE, state=uiconst.UI_HIDDEN, idx=0)
            setattr(self.sr, '%sBtn' % button, btn)
            btn.OnClick = (func, direction)

        self.sr.nextTOTDBtn.left = self.sr.tipofthedayCaption.textwidth + self.sr.tipofthedayCaption.left + 2



    def ShowIntro(self, *args):
        uthread.pool('GameUI :: GoIntro', sm.GetService('gameui').GoIntro)



    def OpenNews(self, browser, *args):
        uicls.Fill(parent=browser, color=(0.2, 0.2, 0.2, 0.4))
        server = sm.GetService('machoNet').GetTransport('ip:packet:server') and sm.GetService('machoNet').GetTransport('ip:packet:server').transport.address.lower()
        if boot.region == 'optic':
            browser.GoTo('http://eve.gtgame.com.cn/gamenews/index.htm')
        else:
            browser.GoTo('http://www.eveonline.com/mb/news.asp?%s' % sm.StartService('patch').GetWebRequestParameters())



    def ClearSlots(self):
        for slot in self.sr.slots:
            slot.SetCaption(localization.GetByLabel('UI/CharacterSelection/EmptySlot'))
            slot.sr.charid = None
            slot.sr.time = None
            slot.sr.rec = None
            slot.sr.icon.state = uiconst.UI_HIDDEN
            slot.sr.delete.state = uiconst.UI_HIDDEN

        t = uiutil.FindChild(slot.parent, 'data')
        c = uiutil.FindChild(slot.parent, 'infoButtonCont')
        if t:
            t.state = uiconst.UI_HIDDEN
        if c:
            c.state = uiconst.UI_HIDDEN



    def LoadCharacters(self, reloadCharacter = False, clearCache = False):
        log.LogInfo('Character selection: Loading the characters')
        if reloadCharacter:
            self.chars = self.GetChars(1)
            blue.pyos.synchro.SleepWallclock(1000)
        self.ClearSlots()
        self.ready = 0
        self.sr.enterBtn.state = uiconst.UI_HIDDEN
        self.sr.prevTOTDBtn.state = self.sr.randomTOTDBtn.state = self.sr.nextTOTDBtn.state = uiconst.UI_HIDDEN
        if not self.chars:
            uthread.new(sm.GetService('gameui').GoCharacterCreation)
        else:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), localization.GetByLabel('UI/CharacterSelection/GettingCharacters'), 1, 6)
            locations = []
            owners = []
            charsByID = {}
            for char in self.chars:
                charsByID[char.characterID] = char

            default = [ char.characterID for char in self.chars ]
            default.sort()
            self.slotOrder = settings.user.ui.Get('charselSlotOrder', default)
            i = 0
            for charID in self.slotOrder:
                if reloadCharacter and clearCache:
                    self.ClearDetails(charID)
                if charID in charsByID:
                    char = charsByID[charID]
                    self.AddCharacter(char, i)
                    i += 1
                    del charsByID[charID]
                else:
                    log.LogWarn('Unknown characterID', charID, charsByID)

            if len(charsByID) and i < 3:
                for (charID, char,) in charsByID.iteritems():
                    char = charsByID[charID]
                    self.AddCharacter(char, i)
                    i += 1

            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Common/Loading'), localization.GetByLabel('UI/CharacterSelection/DoneGettingChars'), 6, 6)
            self.ready = 1
            log.LogInfo('Character selection: Loaded the characters')



    def GetDetails(self, charID):
        if charID in self.details:
            return self.details[charID]
        self.details[charID] = sm.RemoteSvc('charUnboundMgr').GetCharacterToSelect(charID)[0]
        return self.details[charID]



    def ClearDetails(self, charID):
        if charID in self.details:
            del self.details[charID]



    def AddCharacter(self, char, slotidx):
        slot = self.sr.slots[slotidx]
        if slot is None:
            return 
        char.mailCount = None
        char.notificationCount = None
        slot.sr.charid = char.characterID
        slot.sr.time = char.deletePrepareDateTime
        slot.sr.rec = char
        if slotidx == 0:
            uix.Flush(self.sr.infoButtonCont)
            btns = [(localization.GetByLabel('UI/CharacterSelection/Terminate'),
              'ui_4_64_7',
              'terminate',
              self.Terminate,
              10), (localization.GetByLabel('UI/CharacterSelection/AbortTermination'),
              'ui_6_64_9',
              'abortTermination',
              self.UndoTermination,
              10), (localization.GetByLabel('UI/CharacterSelection/CompleteTermination'),
              'ui_6_64_10',
              'completeTermination',
              self.Terminate,
              40)]
            for (caption, icon, button, func, offset,) in btns:
                btn = uix.GetBigButton(24, self.sr.infoButtonCont, const.defaultPadding)
                btn.left = offset
                btn.hint = caption
                btn.OnClick = func
                btn.sr.icon.LoadIcon(icon)
                btn.name = '%sBtn' % button
                uiutil.SetOrder(btn, 0)
                setattr(slot.sr, '%sBtn' % button, btn)
                btn.state = uiconst.UI_HIDDEN
                if button == 'terminate':
                    self.terminateBtn = btn

            slot.sr.textcont = uicls.Container(parent=self.sr.infoButtonCont, name='textCont', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(43, 5, 70, 50))
            slot.sr.countdownText = uicls.EveLabelMedium(text='', parent=slot.sr.textcont, color=None, idx=0, state=uiconst.UI_HIDDEN)
            detailsChar = self.GetDetails(char.characterID)
            char.mailCount = detailsChar.unreadMailCount
            char.eventCount = detailsChar.upcomingEventCount
            char.notificationCount = detailsChar.unprocessedNotifications
            slot.loadPetitions = detailsChar.petitionMessage
            slot.detailsChar = detailsChar
            slot.sr.gender = detailsChar.gender
            slot.SetSmallCaption(char.characterName)
            bloodline = cfg.bloodlines.Get(detailsChar.bloodlineID)
            race = cfg.races.Get(bloodline.raceID)
            dateDiff = (blue.os.GetWallclockTime() - detailsChar.createDateTime) / DAY
            settings.user.ui.Set('bornDaysAgo%s' % char.characterID, dateDiff)
            corpAge = blue.os.GetWallclockTime() - detailsChar.startDateTime
            allAge = None
            corpTicker = cfg.corptickernames.Get(detailsChar.corporationID).tickerName
            (worldSpaceID, stationID, solsysID, constellID, regionID,) = (detailsChar.worldSpaceID,
             detailsChar.stationID,
             detailsChar.solarSystemID,
             detailsChar.constellationID,
             detailsChar.regionID)
            slot.sr.stationID = stationID
            if worldSpaceID:
                location = 'WorldSpace %s' % worldSpaceID
            elif stationID:
                location = cfg.evelocations.Get(stationID).name.split(' - ')[0]
            elif solsysID:
                location = cfg.evelocations.Get(solsysID).name
            else:
                location = 'Unknown'
            if regionID:
                region = cfg.evelocations.Get(regionID).name
            else:
                region = ''
            if constellID:
                constellation = cfg.evelocations.Get(constellID).name
            else:
                constellation = ''
            systemSec = sm.GetService('map').GetSecurityStatus(solsysID)
            locationTxt = '%s - %s / %s / %s' % (systemSec,
             location,
             constellation,
             region)
            if stationID:
                locationTxt += '<br>%s' % localization.GetByLabel('UI/CharacterSelection/DockedInStation', station=stationID)
            if worldSpaceID:
                locationTxt += '<br>%s' % ('Walking around in %s' % cfg.evelocations.Get(worldSpaceID).name)
            (allMemberInfo, allianceID, allianceTicker,) = ('', detailsChar.allianceID, detailsChar.shortName)
            allTicker = ''
            if allianceTicker:
                allTicker = allianceTicker
            allName = ''
            allLogo = ''
            allWidth = 10
            if allianceID:
                allName = cfg.eveowners.Get(allianceID).name
                allAge = blue.os.GetWallclockTime() - detailsChar.allianceMemberStartDate
                allWidth = 80
                allLogo = '\n                                <td width=64>\n                                    <img width=64 height=64 src=alliancelogo:%s alt="%s"><br> \n                                </td>\n                            ' % (allianceID, allName)
                allMemberInfo = '\n                                    <b>%s [%s]</b>\n                                    <br>\n                                    %s\n                                ' % (allName, allianceTicker, localization.GetByLabel('UI/CharacterSelection/MemberFor', memberTime=util.FmtTimeInterval(allAge, 'day')))
            bounty = ''
            if detailsChar.bounty:
                bounty = '\n                <tr>\n                    <td width=80><div style="font:%(fontSize)s; letter-spacing:%(letterspace)s; font-weight: bold;">%(bountyText)s</div></td>\n                    <td colspan=%(colspan)s><div style="font:%(fontSize)s; letter-spacing:%(letterspace)s";>%(bounty)s</div></td>\n                </tr>\n                ' % {'fontSize': self.fontSize,
                 'bountyText': uiutil.UpperCase(localization.GetByLabel('UI/CharacterSelection/Bounty')),
                 'bounty': util.FmtISK(detailsChar.bounty),
                 'colspan': [1, 2][bool(allianceID)],
                 'letterspace': self.letterspace}
            now = blue.os.GetWallclockTime()
            if detailsChar.skillQueueEndTime and now < detailsChar.skillQueueEndTime:
                time = detailsChar.skillQueueEndTime - now
                timeString = util.FmtDate(time, 'ls')
                sp = localization.GetByLabel('UI/CharacterSelection/TrainingQueueFinishesIn', numSkillpoints=detailsChar.skillPoints, finishTime=timeString)
            else:
                sp = localization.GetByLabel('UI/CharacterSelection/TrainingQueueInactive', numSkillpoints=detailsChar.skillPoints)
            shipName = ''
            if detailsChar.shipTypeID:
                shipName = cfg.invtypes.Get(detailsChar.shipTypeID).name
            if detailsChar.shipName:
                shipNameStripped = detailsChar.shipName.replace('&', '&amp;')
                shipName = '%s<br>[%s]' % (shipName, shipNameStripped)
            txt = '\n            <table width=%(width)s cellpadding=1 cellspacing=6>\n                <tr>\n                    <td width=64>\n                        <img width=64 height=64 src=racelogo:%(raceid)s alt="%(racename)s"><br>\n                    </td>\n                    <td valign="middle">\n                        <font size=24>%(charname)s<br></font>\n                        <font size=12>%(title)s</font>\n                        <font size=:%(fontSize)s>\n                   </td>\n                </tr>\n                <tr>\n                    <td colspan=3>\n                    <hr>\n                    <font size=1>\n                    <br>\n                    </td>\n                </tr>\n                <tr>\n                    <td width=64>\n                        <img width=64 height=64 src=corplogo:%(corpid)s alt="%(corpname)s"><br>\n                    </td>\n                    <td valign="middle">\n                        <div style="font:%(fontSize)s; letter-spacing:%(letterspace)s;">                    \n                        <b>%(corpName)s [%(corpTicker)s]</b>\n                        <br>\n                        %(memberFor)s\n                        <br>\n                        <br>\n                        %(allmemberinfo)s\n                    </div>\n                    </td>\n                    \n                    %(alllogo)s\n                    \n                </tr>\n                <tr>\n                    <td colspan=3>\n                    <font size=1>\n                    <br>\n                    <hr>\n                    <br>\n                    </td>\n                </tr>\n                <tr>\n                    <td><div style="font:%(fontSize)s; letter-spacing:1;">%(loc)s</div></td>\n                    <td colspan=%(colspan)s><div style="font:%(fontSize)s; letter-spacing:%(letterspace)s;">%(location)s</div></td>\n                </tr>\n                <tr>\n                    <td><div style="font:%(fontSize)s; letter-spacing:1;">%(acitveShip)s</div></td>\n                    <td colspan=%(colspan)s><div style="font:%(fontSize)s; letter-spacing:%(letterspace)s;">%(ship)s</div></td>\n                </tr>\n                <tr>\n                    <td><div style="font:%(fontSize)s; letter-spacing:1;">%(skillpoints)s</div></td>\n                    <td colspan=%(colspan)s><div style="font:%(fontSize)s; letter-spacing:%(letterspace)s;">%(sp)s</div></td>\n                </tr>\n                <tr>\n                    <td><div style="font:%(fontSize)s; letter-spacing:1;">%(weal)s</div></td>\n                    <td colspan=%(colspan)s>\n                    <div style="font:%(fontSize)s; letter-spacing:%(letterspace)s;">%(wealth)s</div>><br/>\n                    <div style="font:%(fontSize)s; letter-spacing:%(letterspace)s;">%(aurWealth)s</div>\n                    </td>\n                </tr>\n                <tr>\n                    <td width=80><div style="font:%(fontSize)s; letter-spacing:1;">%(secstat)s</div></td>\n                    <td colspan=%(colspan)s><div style="font:%(fontSize)s; letter-spacing:%(letterspace)s;">%(security)2.1f</div></td>\n                </tr>\n                %(bounty)s\n                <tr>\n                    <td colspan=3>\n                    <hr>\n                    </td>\n                </tr>\n            ' % {'corpName': cfg.eveowners.Get(detailsChar.corporationID).name,
             'corpTicker': corpTicker,
             'memberFor': localization.GetByLabel('UI/CharacterSelection/MemberFor', memberTime=util.FmtTimeInterval(corpAge, 'day')),
             'allmemberinfo': allMemberInfo,
             'security': detailsChar.securityRating,
             'secstat': localization.GetByLabel('UI/CharacterSelection/InfoSecurityStatus'),
             'location': locationTxt,
             'loc': localization.GetByLabel('UI/CharacterSelection/InfoLocation'),
             'weal': localization.GetByLabel('UI/CharacterSelection/InfoWealth'),
             'charname': char.characterName,
             'corpid': detailsChar.corporationID,
             'raceid': race.raceID,
             'racename': race.raceName,
             'title': detailsChar.title,
             'width': self.infoWidth,
             'bounty': bounty,
             'skillpoints': localization.GetByLabel('UI/CharacterSelection/InfoSkills'),
             'sp': sp,
             'acitveShip': localization.GetByLabel('UI/CharacterSelection/ActiveShip'),
             'ship': shipName,
             'sp': sp,
             'wealth': util.FmtISK(detailsChar.balance),
             'aurWealth': util.FmtAUR(detailsChar.aurBalance),
             'corpname': cfg.eveowners.Get(detailsChar.corporationID).name,
             'alllogo': allLogo,
             'fontSize': self.fontSize,
             'colspan': [1, 2][bool(allianceID)],
             'letterspace': self.letterspace}
            warningText = None
            warningTitle = None
            if detailsChar.daysLeft is not None:
                if detailsChar.userType == 23 and detailsChar.daysLeft <= 3:
                    warningText = localization.GetByLabel('UI/CharacterSelection/SubscriptionWarningTrial', daysLeft=detailsChar.daysLeft)
                    warningTitle = localization.GetByLabel('UI/CharacterSelection/SubscriptionWarningTrialHeader')
                elif detailsChar.daysLeft <= 10:
                    warningText = localization.GetByLabel('UI/CharacterSelection/SubscriptionWarning', daysLeft=detailsChar.daysLeft)
                    warningTitle = localization.GetByLabel('UI/CharacterSelection/SubscriptionWarningHeader')
            if warningText is not None:
                txt += '\n                    <tr>\n                        <td colspan=3><div><font size=15 color=0xeeca00>%(subscrWarnTitle)s<br></font>\n                        <font size=12>%(subscrWarn)s<br></font>\n                    </div></td></tr>\n                    <tr><td colspan=3>\n                        <hr>\n                    </td></tr>\n                    </table></font>\n                    ' % {'subscrWarnTitle': warningTitle,
                 'subscrWarn': warningText}
            else:
                txt += '</table></font>'
            self.sr.editControl.xmargin = 0
            self.sr.editControl.LoadHTML(txt)
            if not self or self.destroyed:
                return 
            editContentHeight = self.sr.editControl.GetContentHeight()
            self.sr.infoParent.height = editContentHeight + 26
            self.countDownTimer = None
            if slot.sr.time:
                slot.sr.abortTerminationBtn.state = uiconst.UI_NORMAL
                if slot.sr.time > blue.os.GetWallclockTime():
                    self.countDownTimer = None
                    self.UpdateCountDown(slot.sr.time)
                    self.countDownTimer = base.AutoTimer(1000, self.UpdateCountDown, slot.sr.time)
                else:
                    slot.sr.completeTerminationBtn.state = uiconst.UI_NORMAL
                if self.sr.redeemBtn.state == uiconst.UI_NORMAL:
                    self.sr.redeemBtn.state = uiconst.UI_HIDDEN
            else:
                self.sr.enterBtn.state = uiconst.UI_NORMAL
                slot.sr.terminateBtn.state = uiconst.UI_NORMAL
                slot.sr.countdownText.state = uiconst.UI_HIDDEN
                self.countDownTimer = None
                if len(self.redeemTokens) > 0:
                    self.sr.redeemBtn.state = uiconst.UI_NORMAL
                    self.sr.redeemBtn.hint = localization.GetByLabel('UI/CharacterSelection/CanRedeemItems', num=len(self.redeemTokens))
            self.sr.prevTOTDBtn.state = self.sr.randomTOTDBtn.state = self.sr.nextTOTDBtn.state = uiconst.UI_NORMAL
            self.sr.tipofthedayText.state = uiconst.UI_NORMAL
            slot.sr.activity.state = uiconst.UI_HIDDEN
            minWidth = 0
            if char.mailCount > 0:
                slot.sr.mail.state = uiconst.UI_DISABLED
                slot.sr.mailText.text = localizationUtil.FormatNumeric(char.mailCount, decimalPlaces=0)
                minWidth = slot.sr.mailText.left + slot.sr.mailText.textwidth + 4
            if char.eventCount > 0:
                slot.sr.calendar.state = uiconst.UI_DISABLED
                slot.sr.calendarText.text = localizationUtil.FormatNumeric(char.eventCount, decimalPlaces=0)
                minWidth = max(slot.sr.calendarText.left + slot.sr.calendarText.textwidth + 4, minWidth)
            if minWidth > 0:
                uiutil.SetOrder(slot.sr.activity, 0)
                slot.sr.activity.state = uiconst.UI_DISABLED
                slot.sr.activity.width = minWidth
        else:
            small = int((self.size - 36) / 2)
            slot.SetSmallCaption(char.characterName, maxWidth=small)
        sm.GetService('photo').GetPortrait(char['characterID'], 512, slot.sr.icon)
        if slot.sr.time:
            slot.sr.icon.color.SetRGB(1.0, 1.0, 1.0, 0.25)
        else:
            slot.sr.icon.color.SetRGB(1.0, 1.0, 1.0, 1.0)
        slot.sr.icon.state = uiconst.UI_DISABLED



    def UpdateCountDown(self, timer):
        timeDiff = timer - blue.os.GetWallclockTime()
        slot = self.sr.slot0
        if timeDiff > 0:
            slot.sr.countdownText.state = uiconst.UI_NORMAL
            if hasattr(slot.sr.countdownText, 'text'):
                slot.sr.countdownText.text = util.FmtTime(timeDiff)
        else:
            slot.sr.countdownText.state = uiconst.UI_HIDDEN
            slot.sr.abortTerminationBtn.state = uiconst.UI_NORMAL
            slot.sr.completeTerminationBtn.state = uiconst.UI_NORMAL
            if hasattr(slot.sr.completeTerminationBtn, 'Blink'):
                slot.sr.completeTerminationBtn.Blink()
            self.countDownTimer = None



    def InitScene(self):
        sm.StartService('sceneManager').LoadScene('res:/dx9/Scene/CharselectScene2.red', 'charsel', leaveUntouched=0, setupCamera=False)



    def GetSlotMenu(self, btn, *args):
        m = []
        if btn.sr.idx == 0:
            if btn.sr.charid:
                if btn.sr.time:
                    if btn.sr.time > blue.os.GetWallclockTime():
                        m += [(localization.GetByLabel('UI/CharacterSelection/RemoveFromBiomass'), self.UndoTermination)]
                    else:
                        m += [(localization.GetByLabel('UI/CharacterSelection/CompleteTermination'), self.Terminate, (btn,))]
                else:
                    m += [(localization.GetByLabel('UI/CharacterSelection/Terminate'), self.Terminate, (btn,))]
            else:
                m += [(localization.GetByLabel('UI/CharacterSelection/CreateNew'), self.CreateNewCharacter)]
        else:
            m += [(localization.GetByLabel('UI/CharacterSelection/SetActive'), self.ChangeSlotOrder, (btn,))]
        return m



    def ChangeSlotOrder(self, putInFront):
        if self.countDownTimer:
            self.countDownTimer.KillTimer()
        currentOrder = self.slotOrder[:]
        if putInFront.sr.charid in currentOrder:
            currentOrder.remove(putInFront.sr.charid)
        currentOrder.insert(0, putInFront.sr.charid)
        settings.user.ui.Set('charselSlotOrder', currentOrder)
        self.slotOrder = currentOrder
        self.LoadCharacters()



    def SelectSlot(self, slot, *args):
        if not self.ready:
            log.LogInfo('Character selection: Denied character selection, not ready')
            eve.Message('Busy')
            return 
        sm.StartService('redeem').CloseRedeemWindow()
        if slot.sr.charid is None:
            if len(self.chars) == 2 and sm.RemoteSvc('charUnboundMgr').IsUserReceivingCharacter():
                eve.Message('UserReceivingCharacter')
                return 
            sm.GetService('jumpQueue').PrepareQueueForCharID(None)
            self._CharSelection__Say(None)
            self.CreateNewCharacter()
            return 
        if slot.sr.idx != 0:
            sm.GetService('jumpQueue').PrepareQueueForCharID(None)
            self._CharSelection__Say(None)
            self.ChangeSlotOrder(slot)
            return 
        if slot.sr.time:
            questionHeader = localization.GetByLabel('UI/CharacterSelection/UndoRecycleRequest')
            questionText = localization.GetByLabel('UI/CharacterSelection/UndoRecycleRequestText', charID=slot.sr.charid)
            if eve.Message('CustomQuestion', {'header': questionHeader,
             'question': questionText}, uiconst.YESNO) == uiconst.ID_YES:
                self.UndoTermination()
            return 
        self.Confirm()



    def ReduceCharacterGraphics(self):
        prefs.SetValue('fastCharacterCreation', 1)
        prefs.SetValue('charClothSim', 0)
        prefs.SetValue('charTextureQuality', 2)
        prefs.SetValue('shaderQuality', 1)
        prefs.SetValue('textureQuality', 1)



    def CreateNewCharacter(self, *args):
        if not self.ready:
            eve.Message('Busy')
            return 
        lowEnd = sm.GetService('device').CheckIfLowEndGraphicsDevice()
        msg = uiconst.ID_YES
        if not sm.StartService('device').SupportsSM3():
            msg = eve.Message('AskMissingSM3', {}, uiconst.YESNO, default=uiconst.ID_NO)
        if msg != uiconst.ID_YES:
            return 
        msg = uiconst.ID_YES
        if not lowEnd and ccUtil.SupportsHigherShaderModel():
            msg = eve.Message('AskUseLowShader', {}, uiconst.YESNO, default=uiconst.ID_NO)
        if msg != uiconst.ID_YES:
            return 
        if lowEnd:
            msg2 = uiconst.ID_NO
            msg2 = eve.Message('ReduceGraphicsSettings', {}, uiconst.YESNO, default=uiconst.ID_NO)
            if msg2 == uiconst.ID_YES:
                self.ReduceCharacterGraphics()
        sm.StartService('redeem').CloseRedeemWindow()
        eve.Message('CCNewChar')
        if self.wnd:
            self.wnd.state = uiconst.UI_HIDDEN
        uthread.new(sm.GetService('gameui').GoCharacterCreation, askUseLowShader=0)



    def CreateNewAvatar(self, charID, gender, bloodlineID, dollState, *args):
        self.ClearDetails(charID)
        uthread.new(sm.GetService('gameui').GoCharacterCreation, charID, gender, bloodlineID, dollState=dollState)



    def Redeem(self, *args):
        charID = self.sr.slot0.sr.charid
        stationID = self.sr.slot0.sr.stationID
        if charID is None:
            raise UserError('RedeemNoCharacter')
        sm.StartService('redeem').OpenRedeemWindow(charID, stationID)



    def UndoTermination(self, *args):
        mainSlot = self.sr.slot0
        sm.RemoteSvc('charUnboundMgr').CancelCharacterDeletePrepare(mainSlot.sr.charid)
        self.LoadCharacters(1)



    def Terminate(self, *args):
        if not self.ready:
            eve.Message('Busy')
            return 
        mainSlot = self.sr.slot0
        try:
            self.ready = 0
            charID = mainSlot.sr.charid
            if mainSlot.sr.time:
                if mainSlot.sr.time < blue.os.GetWallclockTime():
                    eve.Message('CCTerminate')
                    if eve.Message('AskDeleteCharacter', {'charID': charID}, uiconst.YESNO) == uiconst.ID_YES:
                        sm.StartService('redeem').CloseRedeemWindow()
                        progressHeader = localization.GetByLabel('UI/CharacterSelection/RecyclingCharacter', charID=mainSlot.sr.charid)
                        sm.GetService('loading').ProgressWnd(progressHeader, '', 1, 2)
                        try:
                            eve.Message(('CCTerminateForGoodFemaleBegin', 'CCTerminateForGoodMaleBegin')[mainSlot.sr.gender])
                            error = sm.RemoteSvc('charUnboundMgr').DeleteCharacter(mainSlot.sr.charid)
                            eve.Message(('CCTerminateForGoodFemale', 'CCTerminateForGoodMale')[mainSlot.sr.gender])

                        finally:
                            sm.GetService('loading').ProgressWnd(progressHeader, '', 2, 2)
                            self.ready = 1

                        if error:
                            apply(eve.Message, error)
                            return 
                        self.LoadCharacters(1)
                else:
                    infoMsg = localization.GetByLabel('UI/CharacterSelection/AlreadyInBiomassQueue', charID=charID, timeLeft=mainSlot.sr.time - blue.os.GetWallclockTime())
                    eve.Message('CustomInfo', {'info': infoMsg})
            elif eve.Message('AskSubmitToBiomassQueue', {'charID': charID}, uiconst.YESNO) == uiconst.ID_YES:
                ret = sm.RemoteSvc('charUnboundMgr').PrepareCharacterForDelete(mainSlot.sr.charid)
                if ret:
                    eve.Message('SubmitToBiomassQueueConfirm', {'charID': charID,
                     'when': ret - blue.os.GetWallclockTime()})
                    self.LoadCharacters(1)

        finally:
            self.ready = 1




    def Confirm(self, *args):
        if not self.sr.enterBtn or self.sr.enterBtn.state == uiconst.UI_HIDDEN:
            return 
        log.LogInfo('Character selection: Character selection confirmation')
        if not self.ready:
            log.LogInfo('Character selection: Denied character selection confirmation, not ready')
            eve.Message('Busy')
            return 
        sm.StartService('redeem').CloseRedeemWindow()
        for x in xrange(300):
            if not eve.IsClockSynchronizing():
                break
            if x > 30:
                log.general.Log('Clock synchronization still in progress after %d seconds' % x, log.LGINFO)
            blue.pyos.synchro.SleepWallclock(1000)

        if eve.IsClockSynchronizing():
            eve.Message('CustomInfo', {'info': 'Clock synchronization in progress.  Please wait.'})
            return 
        mainSlot = self.sr.slot0
        if not mainSlot or not mainSlot.sr.charid:
            eve.Message('SelectCharacter')
            return 
        if sm.GetService('jumpQueue').GetPreparedQueueCharID() != mainSlot.sr.charid:
            self._CharSelection__Confirm(mainSlot.sr.charid)



    def __Confirm(self, charID, secondChoiceID = None):
        self.terminateBtn.state = uiconst.UI_HIDDEN
        dollState = self.sr.slot0.detailsChar.paperDollState
        sm.GetService('cc').StoreCurrentDollState(dollState)
        if dollState in (const.paperdollStateForceRecustomize, const.paperdollStateNoExistingCustomization):
            if dollState == const.paperdollStateForceRecustomize:
                eve.Message('ForcedPaperDollRecustomization')
            dc = self.sr.slot0.detailsChar
            self.CreateNewAvatar(charID, dc.gender, dc.bloodlineID, dollState=dollState)
            return 
        self.ready = 0
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterSelection/CharacterSelection'), localization.GetByLabel('UI/CharacterSelection/EnterGameAs', char=charID), 1, 2)
        try:
            eve.Message('OnCharSel')
            sm.GetService('jumpQueue').PrepareQueueForCharID(charID)
            try:
                if not eve.session.role & service.ROLE_NEWBIE and settings.user.ui.Get('bornDaysAgo%s' % charID, 0) > 30:
                    settings.user.ui.Set('doTutorialDungeon%s' % charID, 0)
                loadDungeon = settings.user.ui.Get('doTutorialDungeon%s' % charID, 1)
                sm.GetService('sessionMgr').PerformSessionChange('charsel', sm.RemoteSvc('charUnboundMgr').SelectCharacterID, charID, loadDungeon, secondChoiceID)
                settings.user.ui.Set('doTutorialDungeon%s' % charID, 0)
                settings.user.ui.Set('doTutorialDungeon', 0)
            except UserError as e:
                self.terminateBtn.state = uiconst.UI_NORMAL
                if e.msg == 'SystemCheck_SelectFailed_Full':
                    solarSystemID = e.args[1]['system'][1]
                    self.SelectAlternativeSolarSystem(charID, solarSystemID, secondChoiceID)
                    return 
                if e.msg != 'SystemCheck_SelectFailed_Queued':
                    sm.GetService('jumpQueue').PrepareQueueForCharID(None)
                    raise 
            except:
                sm.GetService('jumpQueue').PrepareQueueForCharID(None)
                self.terminateBtn.state = uiconst.UI_NORMAL
                raise 
        except:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterSelection/CharacterSelection'), localization.GetByLabel('UI/CharacterSelection/Failed'), 2, 2)
            sm.GetService('loading').FadeFromBlack()
            self.ready = 1
            self.terminateBtn.state = uiconst.UI_NORMAL
            raise 
        if self.sr.slot0 and self.sr.slot0.sr.charid:
            if self.sr.slot0.loadPetitions:
                uthread.new(sm.GetService('petition').CheckNewMessages)
            mailCount = uiutil.GetAttrs(self.sr.slot0, 'sr', 'rec', 'mailCount') or 0
            notificationCount = uiutil.GetAttrs(self.sr.slot0, 'sr', 'rec', 'notificationCount') or 0
            if mailCount + notificationCount > 0:
                uthread.new(sm.GetService('mailSvc').CheckNewMessages, mailCount, notificationCount)



    def SelectAlternativeSolarSystem(self, charID, solarSystemID, secondChoiceID = None):
        map = sm.StartServiceAndWaitForRunningState('map')
        neighbors = map.GetNeighbors(solarSystemID)
        if secondChoiceID is None:
            selectText = localization.GetByLabel('UI/CharacterSelection/SelectAlternativeSystem')
        else:
            selectText = localization.GetByLabel('UI/CharacterSelection/SelectAnotherAlternativeSystem')
            neighbors.extend(map.GetNeighbors(secondChoiceID))
        systemSecClass = map.GetSecurityClass(solarSystemID)
        validNeighbors = []
        for ssid in neighbors:
            if ssid == secondChoiceID or ssid == solarSystemID:
                continue
            if map.GetSecurityClass(ssid) == systemSecClass:
                systemItem = map.GetItem(ssid)
                constellationID = systemItem.locationID
                regionID = map.GetRegionForSolarSystem(ssid)
                regionItem = map.GetItem(regionID)
                factionID = regionItem.factionID
                factionName = ''
                if factionID:
                    factionName = cfg.eveowners.Get(factionID).ownerName
                validNeighbors.append(('%s<t>%s<t>%s<t>%s' % (systemItem.itemName,
                  regionItem.itemName,
                  map.GetSecurityStatus(ssid),
                  factionName), ssid, None))

        loadingSvc = sm.StartService('loading')
        loadingSvc.ProgressWnd(localization.GetByLabel('UI/CharacterSelection/CharacterSelection'), localization.GetByLabel('UI/CharacterSelection/Failed'), 2, 2)
        loadingSvc.FadeFromBlack()
        scrollHeaders = [localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
         localization.GetByLabel('UI/Common/LocationTypes/Region'),
         localization.GetByLabel('UI/Common/Security'),
         localization.GetByLabel('UI/Sovereignty/Sovereignty')]
        ret = uix.ListWnd(validNeighbors, None, localization.GetByLabel('UI/CharacterSelection/SystemCongested'), selectText, 1, scrollHeaders=scrollHeaders)
        if ret:
            self._CharSelection__Confirm(charID, ret[1])
        else:
            sm.StartService('jumpQueue').PrepareQueueForCharID(None)
            self.ready = 1



    def Back(self, *args):
        if not self.ready:
            eve.Message('Busy')
            return 
        sm.GetService('connection').Disconnect(1)




