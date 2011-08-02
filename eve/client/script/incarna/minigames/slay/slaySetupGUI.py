import uix
import util
import uicls
import uiutil
import uiconst
import slayConst
import slaycommon
import minigameConst
TEXT_HEIGHT = 16
COMBO_HEIGHT = 22
EDIT_HEIGHT = 25
EDIT_CTRL_HEIGHT = 23
SPACE_HEIGHT = 10
LEFT_START = 10
LEFT_CENTER = 110
LEFT_END = 210

class SlaySetupGUI(uicls.Window):
    __guid__ = 'minigames.SlaySetupGUI'
    default_width = 300
    default_height = 537

    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush



    def SetConfig(self, gameConfig, controller):
        self.controller = controller
        self.gameConfig = gameConfig
        self.gameConfig.selectedColorIndex = 0
        self.Configure()



    def Configure(self):
        self.configured = True
        self.leaveWithoutGamelogicConsequences = False
        self.name = 'slaySetup'
        self.configured = False
        self.gameMasterInitControls = []
        self.messageContainer = None
        self.randomMapCheck = None
        self.submitButton = None
        self.selectedMap = slayConst.MAP_TYPE_RANDOM
        self.randomMap = False
        self.startMapSelectionLine = 0
        self.SetWndIcon('40_14')
        self.SetCaption(self.gameConfig.minigameName)
        self.sr.main = uiutil.GetChild(self, 'main')
        uicls.Line(align=uiconst.TOTOP, parent=self.sr.main)



    def GetMainText(self, text, left, top):
        return uicls.Label(text=text, parent=self.sr.main, left=left, top=top, idx=2, fontsize=11, letterspace=1, uppercase=0)



    def SetGameMasterOptions(self):
        self.availableColors = self.gameConfig.availableColors
        self.gameMasterInitControls = []
        line = 5
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_BUY_IN, LEFT_START, line))
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_MIN_ELO, LEFT_CENTER, line))
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_MAX_ELO, LEFT_END, line))
        line += TEXT_HEIGHT
        txt = self.GetMainText(util.FmtISK(self.gameConfig.buyIn), LEFT_START, line)
        txt.bold = 1
        self.gameMasterInitControls.append(txt)
        if self.gameConfig.minElo:
            txt = self.GetMainText('%s' % str(self.gameConfig.minElo), LEFT_CENTER, line)
            txt.bold = 1
            self.gameMasterInitControls.append(txt)
        else:
            txt = self.GetMainText(mls.UI_MINIGAME_NO_LIMIT, LEFT_CENTER, line)
            txt.bold = 1
            self.gameMasterInitControls.append(txt)
        if self.gameConfig.maxElo:
            txt = self.GetMainText('%s' % str(self.gameConfig.maxElo), LEFT_END, line)
            txt.bold = 1
            self.gameMasterInitControls.append(txt)
        else:
            txt = self.GetMainText(mls.UI_MINIGAME_NO_LIMIT, LEFT_END, line)
            txt.bold = 1
            self.gameMasterInitControls.append(txt)
        line += TEXT_HEIGHT * 2
        if not hasattr(self, 'playersConfig'):
            self.playersConfig = []
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_PLAYERS, LEFT_START, line))
        line += TEXT_HEIGHT
        numPlayersDone = 0
        optHuman = mls.UI_MINIGAME_PLAYERTYPE_HUMAN
        optAI = mls.UI_MINIGAME_PLAYERTYPE_AI
        optClosed = mls.UI_MINIGAME_PLAYERTYPE_CLOSED
        addNewCombo = len(self.playersConfig) == 0
        for i in range(0, self.gameConfig.maxPlayers):
            lineDown = False
            if numPlayersDone < self.gameConfig.maxPlayers:
                self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_PLAYER % {'playerNumber': numPlayersDone + 1}, LEFT_START, line + 3))
                if addNewCombo:
                    if numPlayersDone == 0:
                        comboBox = uicls.Combo(label='', parent=self.sr.main, options=((optHuman, minigameConst.PLAYER_TYPE_HUMAN),), configname='', left=57, top=line)
                    elif self.gameConfig.allowAI:
                        comboBox = uicls.Combo(label='', parent=self.sr.main, options=((optHuman, minigameConst.PLAYER_TYPE_HUMAN), (optAI, minigameConst.PLAYER_TYPE_AI), (optClosed, minigameConst.PLAYER_TYPE_NONE)), configname='', left=57, top=line)
                        comboBox.SetValue(minigameConst.PLAYER_TYPE_NONE)
                    else:
                        comboBox = uicls.Combo(label='', parent=self.sr.main, options=((optHuman, minigameConst.PLAYER_TYPE_HUMAN), (optClosed, minigameConst.PLAYER_TYPE_NONE)), configname='', left=57, top=line)
                        comboBox.SetValue(minigameConst.PLAYER_TYPE_NONE)
                    comboBox.name = 'playerOptions'
                    self.playersConfig.append(comboBox)
                numPlayersDone += 1
                lineDown = True
            if numPlayersDone < self.gameConfig.maxPlayers:
                self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_PLAYER % {'playerNumber': numPlayersDone + 1}, 150, line + 3))
                if addNewCombo:
                    if self.gameConfig.allowAI:
                        comboBox = uicls.Combo(label='', parent=self.sr.main, options=((optHuman, minigameConst.PLAYER_TYPE_HUMAN), (optAI, minigameConst.PLAYER_TYPE_AI), (optClosed, minigameConst.PLAYER_TYPE_NONE)), configname='', left=196, top=line)
                    else:
                        comboBox = uicls.Combo(label='', parent=self.sr.main, options=((optHuman, minigameConst.PLAYER_TYPE_HUMAN), (optClosed, minigameConst.PLAYER_TYPE_NONE)), configname='', left=196, top=line)
                        comboBox.name = 'playerOptions'
                    if numPlayersDone == 1 and self.gameConfig.allowAI:
                        comboBox.SetValue(minigameConst.PLAYER_TYPE_AI)
                    else:
                        comboBox.SetValue(minigameConst.PLAYER_TYPE_NONE)
                    self.playersConfig.append(comboBox)
                numPlayersDone += 1
            if lineDown == True:
                line += COMBO_HEIGHT

        sortedColors = []
        for col in self.gameConfig.availableColors:
            sortedColors.append(slaycommon.GetFactionNameByColor(col))

        sortedColors.sort()
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_COLOR, LEFT_START, line))
        line += TEXT_HEIGHT
        options = {}
        for colorEnum in self.gameConfig.availableColors:
            options[slaycommon.GetFactionNameByColor(colorEnum)] = colorEnum

        useOptions = []
        for sortedCol in sortedColors:
            useOptions.append((sortedCol, options[sortedCol]))

        if not hasattr(self, 'selectedPlayerColor'):
            self.selectedPlayerColor = useOptions[self.gameConfig.selectedColorIndex][1]
        selectedIndex = 0
        for entry in useOptions:
            if entry[1] == self.selectedPlayerColor:
                break
            selectedIndex += 1

        if hasattr(self, 'pickColorCombo'):
            self.pickColorCombo.Close()
        self.pickColorCombo = uicls.Combo(label='', parent=self.sr.main, options=useOptions, configname='', left=LEFT_START, top=line)
        self.pickColorCombo.SelectItemByIndex(selectedIndex)
        if hasattr(self, 'playerColor'):
            self.playerColor.Close()
        self.playerColor = uicls.Container(name='selectedColor', parent=self.sr.main, width=40, align=uiconst.RELATIVE, height=self.pickColorCombo.height, left=LEFT_START + self.pickColorCombo.width + 7, top=line)
        uicls.Frame(parent=self.playerColor, color=(0.5, 0.5, 0.5))
        uicls.Fill(parent=self.playerColor, color=slaycommon.ColorEnumToRGB(self.selectedPlayerColor))
        self.pickColorCombo.OnChange = self.OnPickColor
        line += COMBO_HEIGHT
        if self.gameConfig.allowAI:
            self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_AILEVEL, LEFT_START, line))
            line += TEXT_HEIGHT
            comboBox = uicls.Combo(label='', parent=self.sr.main, options=((mls.UI_MINIGAME_SETTINGS_AI_VERY_STUPID, minigameConst.AI_VERY_STUPID),
             (mls.UI_MINIGAME_SETTINGS_AI_STUPID, minigameConst.AI_STUPID),
             (mls.UI_MINIGAME_SETTINGS_AI_CLEVER, minigameConst.AI_CLEVER),
             (mls.UI_MINIGAME_SETTINGS_AI_VERY_CLEVER, minigameConst.AI_VERY_CLEVER)), configname='', left=LEFT_START, top=line)
            comboBox.name = 'aiSetting'
            self.gameMasterInitControls.append(comboBox)
            line += COMBO_HEIGHT
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_TIMER_MODE, LEFT_START, line))
        line += TEXT_HEIGHT
        timerOptions = ((mls.UI_MINIGAME_SIMPLE_TIMER, minigameConst.TIMER_MODE_SIMPLE), (mls.UI_MINIGAME_DELAY_TIMER, minigameConst.TIMER_MODE_DELAYTIMER))
        if not hasattr(self.gameConfig, 'lastSelectedTimeMode'):
            self.gameConfig.lastSelectedTimeMode = minigameConst.TIMER_MODE_SIMPLE
        if self.gameConfig.timerMode == minigameConst.TIMER_MODE_OPTION_NONE:
            timerOptions = ((mls.UI_MINIGAME_NO_TIME_LIMIT, minigameConst.TIMER_MODE_NONE),)
        elif self.gameConfig.timerMode == minigameConst.TIMER_MODE_OPTION_SIMPLE:
            timerOptions = ((mls.UI_MINIGAME_SIMPLE_TIMER, minigameConst.TIMER_MODE_SIMPLE),)
            self.gameConfig.lastSelectedTimeMode = minigameConst.TIMER_MODE_SIMPLE
        elif self.gameConfig.timerMode == minigameConst.TIMER_MODE_OPTION_DELAYTIMER:
            timerOptions = ((mls.UI_MINIGAME_DELAY_TIMER, minigameConst.TIMER_MODE_DELAYTIMER),)
            self.gameConfig.lastSelectedTimeMode = minigameConst.TIMER_MODE_DELAYTIMER
        self.timerCombo = uicls.Combo(label='', parent=self.sr.main, options=timerOptions, configname='', left=LEFT_START, top=line)
        self.timerCombo.SelectItemByValue(self.gameConfig.lastSelectedTimeMode)
        self.timerCombo.name = 'timerSettings'
        self.gameMasterInitControls.append(self.timerCombo)
        line += COMBO_HEIGHT
        if self.gameConfig.lastSelectedTimeMode == minigameConst.TIMER_MODE_SIMPLE:
            self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_TIME_LIMIT_SECONDS, LEFT_START, line))
            line += TEXT_HEIGHT
            timeLimit = uicls.EditPlainText(name='timeLimitSimple', readonly=False, parent=self.sr.main, align=uiconst.RELATIVE, pos=(LEFT_START,
             line,
             40,
             EDIT_CTRL_HEIGHT), padding=(0, 0, 0, 0))
            timeLimit.SetValue(str(self.gameConfig.defaultSimpleTimerSeconds))
            self.gameMasterInitControls.append(timeLimit)
            line += EDIT_HEIGHT
        elif self.gameConfig.lastSelectedTimeMode == minigameConst.TIMER_MODE_DELAYTIMER:
            self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_TIME_LIMIT_DELAY_AMOUNT, LEFT_START, line))
            line += TEXT_HEIGHT
            delayTime = uicls.EditPlainText(name='delayTime', readonly=False, parent=self.sr.main, align=uiconst.RELATIVE, pos=(LEFT_START,
             line,
             40,
             EDIT_CTRL_HEIGHT), padding=(0, 0, 0, 0))
            delayTime.SetValue(str(self.gameConfig.defaultDelayTimerSeconds.preTime))
            self.gameMasterInitControls.append(delayTime)
            mainTime = uicls.EditPlainText(name='mainTime', readonly=False, parent=self.sr.main, align=uiconst.RELATIVE, pos=(60,
             line,
             40,
             EDIT_CTRL_HEIGHT), padding=(0, 0, 0, 0))
            mainTime.SetValue(str(self.gameConfig.defaultDelayTimerSeconds.mainTime))
            self.gameMasterInitControls.append(mainTime)
            line += EDIT_HEIGHT
        self.timerCombo.OnChange = self.OnSelectTimerMode
        if self.gameConfig.bettingAllowed:
            if self.gameConfig.maxBet:
                if self.gameConfig.minBet == self.gameConfig.maxBet:
                    self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_BET_AMOUNT_SPECIFIC % {'amount': util.FmtISK(self.gameConfig.minBet)}, LEFT_START, line))
                else:
                    self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_BET_AMOUNT_MIN_MAX % {'amount1': util.FmtISK(self.gameConfig.minBet),
                     'amount2': util.FmtISK(self.gameConfig.maxBet)}, LEFT_START, line))
            else:
                self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_BET_AMOUNT_NO_MAX % {'amount': util.FmtISK(self.gameConfig.minBet)}, LEFT_START, line))
            line += TEXT_HEIGHT
            if self.gameConfig.minBet != self.gameConfig.maxBet:
                minBet = uicls.EditPlainText(name='minBetAmount', readonly=False, parent=self.sr.main, align=uiconst.RELATIVE, pos=(LEFT_START,
                 line,
                 90,
                 EDIT_CTRL_HEIGHT), padding=(0, 0, 0, 0))
                minBet.SetValue(str(self.gameConfig.minBet))
                self.gameMasterInitControls.append(minBet)
                line += EDIT_HEIGHT
            houseTake = mls.UI_MINIGAME_HOUSE_TAKE_MIN_MAX % {'tax': str(float(self.gameConfig.houseTake * 100)),
             'min': util.FmtISK(self.gameConfig.minBet * self.gameConfig.houseTake),
             'max': util.FmtISK(self.gameConfig.maxBet * self.gameConfig.houseTake)}
            if self.gameConfig.minBet == self.gameConfig.maxBet:
                houseTake = mls.UI_MINIGAME_HOUSE_TAKE_SINGLE % {'tax': str(float(self.gameConfig.houseTake * 100)),
                 'amount': util.FmtISK(self.gameConfig.minBet * self.gameConfig.houseTake)}
            self.gameMasterInitControls.append(self.GetMainText(houseTake, LEFT_START, line))
            line += TEXT_HEIGHT
            self.startMapSelectionLine = line
        if self.gameConfig.maps:
            self.maps = self.UnwrapMapNames(self.gameConfig.maps)
            self.randomMapCheck = uicls.Checkbox(parent=self.sr.main, align=uiconst.RELATIVE)
            self.randomMapCheck.top = line + 3
            self.randomMapCheck.left = 8
            self.randomMapCheck.OnChange = self.MapSelectionsClicked
            self.randomMapCheck.name = 'randomMapCeckbox'
            self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_MAP_RANDOM, 24, line + 4))
            line += COMBO_HEIGHT
            self.startMapSelectionLine = line
            self.randomMap = False
            self.gameMasterInitControls.append(self.randomMapCheck)
        else:
            self.randomMap = True
        line += SPACE_HEIGHT
        self.submitButton = uicls.Button(parent=self.sr.main, label='Submit', func=self.SubmitGameMasterSettings, left=5, top=line, width=100)
        self.submitButton.name = 'submit'
        self.gameMasterInitControls.append(self.submitButton)
        self.MapSelectionsClicked()



    def UnwrapMapNames(self, mapNames):
        names = []
        for entry in mapNames:
            mapNamePart = entry[1]
            mapName = slayConst.slayMessageMapping[entry[0]] % {'name': mapNamePart}
            mapID = entry[2]
            names.append((mapName, mapID))

        return names



    def ShowGameMasterOptions(self, numPlayers, betAmount, players, gameMasterID, availableColors):
        self.gameMasterInitControls = []
        line = 30
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_PLAYER_SETTINGS_WELCOME, LEFT_START, line))
        line += 30
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_PLAYERS, LEFT_START, line))
        leftColumn = True
        for (i, player,) in enumerate(players):
            if leftColumn:
                left = LEFT_START
                line += 17
            else:
                left = 150
            self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_PLAYER % {'playerNumber': i + 1}, left, line))
            if player is None:
                playerName = mls.UI_MINIGAME_SLOT_EMPTY
            elif slaycommon.IsAIPlayer(player):
                playerName = mls.UI_MINIGAME_SLOT_AI
            else:
                playerName = 'Lollar'
                playerName = cfg.eveowners.Get(player).name
            self.gameMasterInitControls.append(self.GetMainText(playerName, left + 45, line))
            leftColumn = not leftColumn

        line += 30
        if betAmount > 0:
            self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_SETTINGS_BETAMOUNT, LEFT_START, line))
            line += 17
            self.gameMasterInitControls.append(self.GetMainText(util.FmtISK(betAmount), LEFT_START, line))
            line += 30
        self.gameMasterInitControls.append(self.GetMainText(mls.UI_MINIGAME_COLOR, LEFT_START, line))
        line += TEXT_HEIGHT
        self.ConfigAvailableColors(availableColors, line)
        uicls.Frame(parent=self.playerColor, color=(0.5, 0.5, 0.5))
        uicls.Fill(parent=self.playerColor, color=slaycommon.ColorEnumToRGB(availableColors[0]))
        line += COMBO_HEIGHT
        self.submitButton = uicls.Button(parent=self.sr.main, label=mls.UI_MINIGAME_SETTINGS_JOIN, func=self.ConfirmJoin, args=('btn1', betAmount), left=5, top=line, width=100)
        self.submitButton.name = 'Join'
        self.gameMasterInitControls.append(self.submitButton)



    def UpdateAvailableColors(self, availableColors):
        pos = self.pickColorCombo.top
        self.pickColorCombo.Close()
        self.playerColor.Close()
        self.ConfigAvailableColors(availableColors, top)



    def ConfigAvailableColors(self, availableColors, pos):
        self.availableColors = availableColors
        self.selectedPlayerColor = availableColors[0]
        options = []
        for color in availableColors:
            options.append((slaycommon.GetFactionNameByColor(color), color))

        self.pickColorCombo = uicls.Combo(label='', parent=self.sr.main, options=options, configname='', left=LEFT_START, top=pos)
        self.playerColor = uicls.Container(name='selectedColor', parent=self.sr.main, width=40, align=uiconst.RELATIVE, height=self.pickColorCombo.height, left=LEFT_START + self.pickColorCombo.width + 7, top=pos)
        self.pickColorCombo.OnChange = self.OnPickColor



    def OnSelectTimerMode(self, *args):
        (control, label, selection,) = args
        if self.gameConfig.lastSelectedTimeMode == minigameConst.TIMER_MODE_SIMPLE:
            self.gameConfig.defaultSimpleTimerSeconds = int(self.FindControl('timeLimitSimple').GetValue())
        elif self.gameConfig.lastSelectedTimeMode == minigameConst.TIMER_MODE_DELAYTIMER:
            self.gameConfig.defaultDelayTimerSeconds = util.KeyVal(preTime=int(self.FindControl('delayTime').GetValue()), mainTime=int(self.FindControl('mainTime').GetValue()))
        self.gameConfig.lastSelectedTimeMode = selection
        self.ClearGameMasterInit()
        self.SetGameMasterOptions()



    def OnPickColor(self, *args):
        (control, label, selection,) = args
        self.selectedPlayerColor = selection
        lastTop = self.playerColor.top
        self.playerColor.Close()
        self.playerColor = uicls.Container(name='selectedColor', parent=self.sr.main, width=40, align=uiconst.RELATIVE, height=self.pickColorCombo.height, left=LEFT_START + self.pickColorCombo.width + 7, top=lastTop)
        uicls.Frame(parent=self.playerColor, color=(0.5, 0.5, 0.5))
        uicls.Fill(parent=self.playerColor, color=slaycommon.ColorEnumToRGB(selection))



    def FindControl(self, name):
        for control in self.gameMasterInitControls:
            if control.name == name:
                return control




    def FindControls(self, name):
        controls = []
        for control in self.gameMasterInitControls:
            if control.name == name:
                controls.append(control)

        return controls



    def MapSelectionsClicked(self, *args):
        line = self.startMapSelectionLine
        toRemove = []
        if self.randomMapCheck:
            self.randomMap = self.randomMapCheck.GetValue() == 1
        if self.randomMap:
            self.selectedMap = slayConst.MAP_TYPE_RANDOM
            for control in self.gameMasterInitControls:
                if control.name in ('preMapText', 'preMap'):
                    toRemove.append(control)
                    control.Close()

            for control in toRemove:
                self.gameMasterInitControls.remove(control)

            tableSizeText = self.GetMainText(mls.UI_MINIGAME_SETTINGS_TABLESIZE, LEFT_START, line)
            tableSizeText.name = 'tableSizeText'
            self.gameMasterInitControls.append(tableSizeText)
            line += TEXT_HEIGHT
            sizeX = uicls.EditPlainText(name='tableSizeX', readonly=False, parent=self.sr.main, align=uiconst.RELATIVE, pos=(LEFT_START,
             line,
             40,
             EDIT_CTRL_HEIGHT), padding=(0, 0, 0, 0))
            if self.gameConfig.defaultMapSizeX is not None:
                sizeX.SetValue(str(self.gameConfig.defaultMapSizeX))
            sizeY = uicls.EditPlainText(name='tableSizeY', readonly=False, parent=self.sr.main, align=uiconst.RELATIVE, pos=(60,
             line,
             40,
             EDIT_CTRL_HEIGHT), padding=(0, 0, 0, 0))
            if self.gameConfig.defaultMapSizeY is not None:
                sizeY.SetValue(str(self.gameConfig.defaultMapSizeY))
            self.gameMasterInitControls.append(sizeX)
            self.gameMasterInitControls.append(sizeY)
            line += EDIT_HEIGHT
            line += SPACE_HEIGHT
            self.submitButton.top = line
        else:
            for control in self.gameMasterInitControls:
                if control.name in ('tableSizeX', 'tableSizeY', 'tableSizeText'):
                    toRemove.append(control)
                    control.Close()

            for control in toRemove:
                self.gameMasterInitControls.remove(control)

            self.selectedMap = self.maps[0][1]
            text = self.GetMainText(mls.UI_MINIGAME_SETTINGS_MAPSELECT, LEFT_START, line)
            text.name = 'preMapText'
            self.gameMasterInitControls.append(text)
            line += TEXT_HEIGHT
            mapsCombo = uicls.Combo(label='', parent=self.sr.main, options=self.maps, configname='', callback=self.OnMapsChange, left=LEFT_START, top=line)
            mapsCombo.width = 150
            mapsCombo.name = 'preMap'
            line += COMBO_HEIGHT
            self.gameMasterInitControls.append(mapsCombo)
            line += SPACE_HEIGHT
            self.submitButton.top = line



    def SubmitGameMasterSettings(self, *args):
        players = []
        aiSetting = minigameConst.AI_VERY_STUPID
        xSize = slayConst.MAX_GAMEWORLD_WIDTH
        ySize = slayConst.MAX_GAMEWORLD_HEIGHT
        if self.randomMap:
            try:
                xSize = int(self.FindControl('tableSizeX').GetValue())
            except:
                raise UserError('MinigameInvalidWidth')
            try:
                ySize = int(self.FindControl('tableSizeY').GetValue())
            except:
                raise UserError('MinigameInvalidHeight')
        for control in self.playersConfig:
            players.append(control.GetValue())

        if self.gameConfig.allowAI:
            aiSetting = int(self.FindControl('aiSetting').GetValue())
        try:
            if not self.gameConfig.bettingAllowed:
                playerBetAmount = 0
            elif self.gameConfig.minBet == self.gameConfig.maxBet:
                playerBetAmount = self.gameConfig.minBet
            else:
                playerBetAmount = int(self.FindControl('minBetAmount').GetValue())
        except:
            raise UserError('MinigameInvalidBet')
        mapType = self.selectedMap
        if players.count(minigameConst.PLAYER_TYPE_HUMAN) < 1:
            raise UserError('MinigameNoHuman')
        if players.count(minigameConst.PLAYER_TYPE_HUMAN) + players.count(minigameConst.PLAYER_TYPE_AI) < 2:
            raise UserError('MinigameNoOpponent')
        timerSettings = None
        if self.gameConfig.lastSelectedTimeMode == minigameConst.TIMER_MODE_SIMPLE:
            timerSettings = int(self.FindControl('timeLimitSimple').GetValue())
        elif self.gameConfig.lastSelectedTimeMode == minigameConst.TIMER_MODE_DELAYTIMER:
            timerSettings = util.KeyVal(delayTime=int(self.FindControl('delayTime').GetValue()), mainTime=int(self.FindControl('mainTime').GetValue()) * 60)
        if xSize < slayConst.SLAY_MIN_WIDTH:
            sm.StartService('gameui').MessageBox(mls.UI_MINIGAME_INFORM_MIN_TABLE_WIDTH % {'size': slayConst.SLAY_MIN_WIDTH}, mls.UI_MINIGAME_INPUT_ERROR_CAPTION)
            return 
        if ySize < slayConst.SLAY_MIN_HEIGHT:
            sm.StartService('gameui').MessageBox(mls.UI_MINIGAME_INFORM_MIN_TABLE_HEIGHT % {'size': slayConst.SLAY_MIN_HEIGHT}, mls.UI_MINIGAME_INPUT_ERROR_CAPTION)
            return 
        if playerBetAmount > 0:
            if eve.Message('ConfirmMinigameBet', {'amount': playerBetAmount,
             'game': self.gameConfig.minigameName}, uiconst.OKCANCEL, uiconst.ID_OK) != uiconst.ID_OK:
                return 
        settings = util.KeyVal(xSize=xSize, ySize=ySize, mapType=mapType, aiSetting=aiSetting, players=players, betAmount=playerBetAmount, timerMode=self.gameConfig.lastSelectedTimeMode, timerSettings=timerSettings, pickedColor=self.selectedPlayerColor)
        self.controller.GameSetup(settings)



    def ShowGameMasterSetup(self):
        uicls.WndCaptionLabel(text=self.gameConfig.minigameName, subcaption=mls.UI_MINIGAME_FANTASY_STRATEGY_CAPTION, parent=self.sr.topParent)
        self.SetGameMasterOptions()



    def ShowJoinGame(self, gameSettings):
        uicls.WndCaptionLabel(text=self.gameConfig.minigameName, subcaption=mls.UI_MINIGAME_FANTASY_STRATEGY_CAPTION, parent=self.sr.topParent)
        self.ShowGameMasterOptions(gameSettings.numPlayers, gameSettings.betAmount, gameSettings.players, gameSettings.gameStarterID, gameSettings.availableColors)



    def ConfirmJoin(self, button, betAmount):
        if betAmount > 0:
            if eve.Message('ConfirmMinigameBet', {'amount': betAmount,
             'game': self.gameConfig.minigameName}, uiconst.OKCANCEL, uiconst.ID_OK) == uiconst.ID_OK:
                self.controller.ConfirmJoinGame(self.selectedPlayerColor)



    def OnMapsChange(self, combo, header, value, *args):
        self.selectedMap = int(value)



    def ClearGameMasterInit(self):
        if self.gameMasterInitControls is not None:
            for control in self.gameMasterInitControls:
                control.Close()

        self.gameMasterInitControls = []



    def CloseQuietly(self):
        self.leaveWithoutGamelogicConsequences = True
        self.Close()



    def OnClose(self, *args):
        if not hasattr(self, 'leaveWithoutGamelogicConsequences'):
            self.Close()
            return 
        if not self.leaveWithoutGamelogicConsequences:
            if self.controller:
                self.controller.LeaveGame()
                self.controller = None
            self.Close()




class MinigameDraggable(uicls.Container):
    __guid__ = 'minigames.MinigameDraggable'

    def __init__(self, *args):
        uicls.Container.__init__(self, *args)
        self.data = {}
        self.gameGui = None
        self.placing = False



    def OnMouseDown(self, *args):
        self.placing = True
        self.gameGui.OnMouseDownGlobal('place', self.data['unitID'])



    def OnMouseMove(self, *args):
        if hasattr(self, 'placing') and self.placing:
            self.gameGui.OnMouseMoveGlobal()



    def OnMouseUp(self, *args):
        if self.placing:
            self.gameGui.OnMouseUpGlobal()




