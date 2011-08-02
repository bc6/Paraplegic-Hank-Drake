import blue
import draw
import copy
import math
import util
import uicls
import uiconst
import uiutil
import random
import cameras
import uthread
import uiconst
import trinity
import slayConst
import minigames
import slaycommon
import minigameConst
import graphicWrappers
from pychartdir import *

class SlayGUI(uicls.Window):
    __guid__ = 'minigames.SlayGUI'
    default_width = 220
    default_height = 517

    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush



    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.mainMessage = []
        self.texts = []
        self.lastMessage = ''
        self.SetWndIcon('40_14')
        self.sr.main = uiutil.GetChild(self, 'main')
        uicls.Line(align=uiconst.TOTOP, parent=self.sr.main)
        self.infoContainer = uicls.Container(name='infoContainer', align=uiconst.RELATIVE, width=200, height=122, left=5, top=5, state=uiconst.UI_NORMAL, parent=self.sr.main)
        self.AddCommonControls()
        cameraService = sm.GetService('cameraClient')
        self.slayCamera = cameraService.GetActiveCamera()
        self.mouseOverTile = None
        self.mouseUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnMouseUpGlobal)
        self.mouseDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnMouseDownGlobal)
        self.mouseMoveCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnMouseMoveGlobal)
        self.dragIconMade = False
        self.dragIcon = None
        self.placing = False
        dev = trinity.GetDevice()
        self.scene = uicore.desktop
        uicls.Frame(parent=self.infoContainer)



    def SetConfig(self, settings, controller):
        self.modelsManager = None
        self.controller = controller
        self.mouseUpCookie = None
        self.mouseDownCookie = None
        self.mouseMoveCookie = None
        self.turnSeconds = 0
        self.gameSeconds = 0
        self.gameMinutes = 0
        self.turnCounterCountUp = True
        self.timePart = None
        self.modelsManager = None
        self.running = True
        self.clearTiles = True
        self.doNotFade = False
        self.turnCounterText = None
        self.delayCounterText = None
        self.mainCounterText = None
        self.storedTableData = None
        self.dragUnit = None
        self.dragModel = None
        self.chart = None
        self.lastChartData = None
        self.lastHightlightetUnit = None
        self.playersInfo = {}
        self.ownerColors = {}
        self.infoChildren = []
        self.savedCamBehaviours = []
        self.numTiles = 0
        self.numTiles = 0
        self.settings = settings
        self.SetCaption(self.settings.minigameName)
        if self.settings.timerMode == minigameConst.TIMER_MODE_SIMPLE:
            self.ResetTurnCounter(self.settings.timerMode, self.settings.timerSettings)
        uthread.new(self.MainCounter)
        uthread.new(self.TurnCounter)



    def AddCommonControls(self, *args):
        self.messageContainer = uicls.Container(name='messageContainer', align=uiconst.RELATIVE, width=200, height=23, left=5, top=132, state=uiconst.UI_NORMAL, parent=self.sr.main)
        uicls.Frame(parent=self.messageContainer)
        pos = 0
        for i in xrange(0, 12):
            self.mainMessage.append(uicls.Label(text='', parent=self.messageContainer, left=4, top=pos + 2, idx=2, fontsize=11, letterspace=1, uppercase=0))
            self.texts.append(('', (1.0, 1.0, 1.0, 1.0)))
            pos += 9

        line = 337
        uicls.Button(parent=self.sr.main, label=mls.UI_MINIGAME_GIVE_UP, func=self.OnGiveUp, left=132, top=line)
        line += 20
        uicls.Button(parent=self.sr.main, label=mls.UI_MINIGAME_UNDO, func=self.OnUndo, left=132, top=line)
        line += 20
        uicls.Button(parent=self.sr.main, label=mls.UI_MINIGAME_PLACE_BET, func=self.OnPlaceRunningBet, left=132, top=line)
        line += 20
        uicls.Button(parent=self.sr.main, label=mls.UI_SHARED_HELP, func=self.OnHelp, left=132, top=line)
        line += 27
        uicls.Button(parent=self.sr.main, label=mls.UI_MINIGAME_END_TURN, func=self.OnTurn, left=1, top=line)
        if len(self.lastMessage):
            self.AddMessage(self.lastMessage, minigameConst.MESSAGE_NORMAL)
        if not hasattr(self, 'playerInfoContainer'):
            self.playerInfoContainer = uicls.Container(name='playerInfoContainer', align=uiconst.RELATIVE, width=200, height=168, left=5, top=160, state=uiconst.UI_NORMAL, parent=self.sr.main)
            uicls.Frame(parent=self.playerInfoContainer)
        self.unitInfoContainer = uicls.Container(name='unitInfoContainer', align=uiconst.RELATIVE, width=200, height=87, left=5, top=333, state=uiconst.UI_NORMAL, parent=self.sr.main)
        uicls.Frame(parent=self.unitInfoContainer)
        uicls.Label(text=mls.UI_MINIGAME_SUPPORT_COST, parent=self.unitInfoContainer, left=4, top=1, idx=2, fontsize=10, letterspace=1, uppercase=1)
        peasantContainer = uicls.Container(name='peasantContainer', align=uiconst.RELATIVE, width=32, height=32, left=4, top=14, state=uiconst.UI_NORMAL, parent=self.unitInfoContainer)
        peasantSprite = uicls.Sprite(name='peasantSprite', parent=peasantContainer, texturePath=self.GetRes(slayConst.OCCUPY_PEASANT), align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0))
        uicls.Label(text=str(slayConst.SUPPORT_COST_PEASANT), parent=self.unitInfoContainer, left=38, top=23, idx=2, fontsize=12, letterspace=1, uppercase=1)
        spearmanContainer = uicls.Container(name='spearmanContainer', align=uiconst.RELATIVE, width=32, height=32, left=60, top=14, state=uiconst.UI_NORMAL, parent=self.unitInfoContainer)
        spearmanSprite = uicls.Sprite(name='spearmanSprite', parent=spearmanContainer, texturePath=self.GetRes(slayConst.OCCUPY_SPEARMAN), align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0))
        uicls.Label(text=str(slayConst.SUPPORT_COST_SPEARMAN), parent=self.unitInfoContainer, left=93, top=23, idx=2, fontsize=12, letterspace=1, uppercase=1)
        knightContainer = uicls.Container(name='knightContainer', align=uiconst.RELATIVE, width=32, height=32, left=4, top=52, state=uiconst.UI_NORMAL, parent=self.unitInfoContainer)
        knightSprite = uicls.Sprite(name='knightSprite', parent=knightContainer, texturePath=self.GetRes(slayConst.OCCUPY_KNIGHT), align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0))
        uicls.Label(text=str(slayConst.SUPPORT_COST_KNIGHT), parent=self.unitInfoContainer, left=38, top=60, idx=2, fontsize=12, letterspace=1, uppercase=1)
        baronContainer = uicls.Container(name='baronContainer', align=uiconst.RELATIVE, width=32, height=32, left=60, top=52, state=uiconst.UI_NORMAL, parent=self.unitInfoContainer)
        baronSprite = uicls.Sprite(name='baronSprite', parent=baronContainer, texturePath=self.GetRes(slayConst.OCCUPY_BARON), align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0))
        uicls.Label(text=str(slayConst.SUPPORT_COST_BARON), parent=self.unitInfoContainer, left=93, top=60, idx=2, fontsize=12, letterspace=1, uppercase=1)



    def OnPlaceRunningBet(self, *args):
        uthread.new(self.controller.Action, slayConst.INQUIRE_PLACE_RUNNING_BET)



    def InsertDragModel(self, unitID, x, y, placing = False):
        insertParent = uicore.layer.modal
        self.dragModel = uicls.Container(name='dragIcon', idx=0, align=uiconst.RELATIVE, width=52, height=52, parent=insertParent)
        self.dragModel.left = x - int(self.dragModel.width / 2)
        self.dragModel.top = y - self.dragModel.height
        spriteID = str(unitID)
        sprite = uicls.Sprite(name=spriteID, parent=self.dragModel, texturePath=self.GetRes(unitID), align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0))
        sprite.name = str(unitID)
        self.slayCamera.freeze = True



    def OnMouseMoveGlobal(self, *args):
        x = uicore.uilib.x
        y = uicore.uilib.y
        if self.dragModel:
            self.dragModel.left = x - int(self.dragModel.width / 2)
            self.dragModel.top = y - self.dragModel.height
            self.modelsManager.HighlightSelected(x, y)
        return True



    def OnMouseDownGlobal(self, *args):
        if self.destroyed:
            return 
        x = uicore.uilib.x
        y = uicore.uilib.y
        if hasattr(args[0], '__guid__') and args[0].__guid__ == 'minigames.MinigameDraggable':
            return True
        if len(args) > 0 and args[0] == 'place':
            self.placing = True
            self.InsertDragModel(args[1], x, y, True)
            self.dragUnit = args[1]
            if self.dragUnit == slayConst.OCCUPY_PEASANT:
                self.controller.CalcPossibleMovesUsingCurrSelectedArea()
        else:
            picking = self.modelsManager.IsPickingInGame(x, y)
            if picking:
                self.controller.PlaySound('mouseDown')
                self.dragUnit = self.modelsManager.GetPickedEntity()
                if self.dragUnit is not None and self.dragUnit.owner == session.charid and self.dragUnit.occupier.unitID in [slayConst.OCCUPY_PEASANT,
                 slayConst.OCCUPY_SPEARMAN,
                 slayConst.OCCUPY_KNIGHT,
                 slayConst.OCCUPY_BARON]:
                    if not self.dragUnit.active:
                        return True
                    if self.dragUnit.occupier.unitID == slayConst.OCCUPY_PEASANT:
                        self.InsertDragModel(slayConst.OCCUPY_PEASANT, x, y)
                    elif self.dragUnit.occupier.unitID == slayConst.OCCUPY_SPEARMAN:
                        self.InsertDragModel(slayConst.OCCUPY_SPEARMAN, x, y)
                    elif self.dragUnit.occupier.unitID == slayConst.OCCUPY_KNIGHT:
                        self.InsertDragModel(slayConst.OCCUPY_KNIGHT, x, y)
                    elif self.dragUnit.occupier.unitID == slayConst.OCCUPY_BARON:
                        self.InsertDragModel(slayConst.OCCUPY_BARON, x, y)
                    self.controller.CalcPossibleMoves(self.dragUnit.x, self.dragUnit.y)
                    self.controller.TileClick(self.dragUnit.x, self.dragUnit.y)
                elif self.dragUnit:
                    self.controller.TileClick(self.dragUnit.x, self.dragUnit.y)
                    self.dragUnit = None
            else:
                self.dragUnit = None
        return True



    def OnMouseUpGlobal(self, *args):
        if self.destroyed:
            return 
        x = uicore.uilib.x
        y = uicore.uilib.y
        self.mouseOverTile = None
        picking = self.modelsManager.IsPickingInGame(x, y)
        if picking:
            self.slayCamera.freeze = False
            self.controller.PlaySound('mouseUp')
            if self.placing:
                destination = self.modelsManager.GetPickedEntity()
                if destination is not None:
                    if self.dragUnit == slayConst.OCCUPY_PEASANT:
                        uthread.new(self.controller.Action, slayConst.PLACE_UNIT, (destination.x, destination.y))
                    else:
                        uthread.new(self.controller.Action, slayConst.PLACE_CASTLE, (destination.x, destination.y))
            elif self.dragUnit is not None:
                self.controller.TileClick(self.dragUnit.x, self.dragUnit.y)
                if not self.modelsManager:
                    return 
                destination = self.modelsManager.GetPickedEntity()
                if destination and self.dragUnit and destination.tileID != self.dragUnit.tileID:
                    uthread.new(self.controller.Action, slayConst.MOVE_UNIT, (self.dragUnit.x,
                     self.dragUnit.y,
                     destination.x,
                     destination.y))
        self.dragging = False
        self.dragUnit = None
        self.placing = False
        self.modelsManager.RefreshMouseMoveTile(None)
        if self.dragModel:
            self.dragModel.Close()
            self.dragModel = None
        self.modelsManager.SetPossibleMovesHighlight([])
        return True



    def ResetHighlights(self):
        self.modelsManager.SetPossibleMovesHighlight([])
        self.modelsManager.RefreshMouseMoveTile(None)
        if self.dragModel is not None:
            self.dragModel.Close()
            self.dragModel = None
        self.dragUnit = None



    def OnClose(self, *args):
        if hasattr(self, 'dragModel'):
            if self.dragModel:
                self.dragModel.Close()
                self.dragModel = None
            self.running = False
            if self.mouseUpCookie:
                uicore.event.UnregisterForTriuiEvents(self.mouseUpCookie)
            if self.mouseDownCookie:
                uicore.event.UnregisterForTriuiEvents(self.mouseDownCookie)
            if self.mouseMoveCookie:
                uicore.event.UnregisterForTriuiEvents(self.mouseMoveCookie)
            self.running = False
            if self.controller:
                self.controller.LeaveGame()
        self.Close()



    def ResetTurnCounter(self, timerMode, utcTimerOver, timePart = None, mainTime = 0):
        self.timePart = timePart
        if timerMode == minigameConst.TIMER_MODE_SIMPLE:
            self.turnCounterCountUp = False
            self.turnSeconds = blue.os.TimeAsDouble(utcTimerOver - blue.os.GetTime())
        elif timerMode == minigameConst.TIMER_MODE_DELAYTIMER:
            self.turnCounterCountUp = False
            self.turnSeconds = blue.os.TimeAsDouble(utcTimerOver - blue.os.GetTime())
            self.mainTimeSeconds = mainTime
        else:
            self.turnCounterCountUp = True
            self.turnSeconds = 0



    def TurnCounter(self):
        try:
            while self.running:
                if self.turnCounterCountUp:
                    self.turnSeconds += 1
                else:
                    self.turnSeconds -= 1
                (minutes, seconds,) = self.ToMinutesAndSeconds(self.turnSeconds)
                time = '%s:%s' % (minutes, seconds)
                if self.turnSeconds < 0:
                    time = '00:00'
                if self.turnCounterText is not None:
                    self.turnCounterText.Close()
                if self.delayCounterText is not None:
                    self.delayCounterText.Close()
                if self.timePart == minigameConst.TIMER_DELAYTIME:
                    (mainMinutes, mainSeconds,) = self.ToMinutesAndSeconds(self.mainTimeSeconds)
                    mainTime = '%s:%s' % (mainMinutes, mainSeconds)
                    self.turnCounterText = uicls.Label(text=mainTime, parent=self.sr.topParent, left=183, top=12, idx=2, fontsize=10, letterspace=1, uppercase=1)
                    self.delayCounterText = uicls.Label(text=time, parent=self.sr.topParent, left=153, top=12, idx=2, fontsize=10, letterspace=1, uppercase=1)
                elif self.timePart == minigameConst.TIMER_MAINTIME:
                    self.turnCounterText = uicls.Label(text=time, parent=self.sr.topParent, left=183, top=12, idx=2, fontsize=10, letterspace=1, uppercase=1)
                    self.delayCounterText = uicls.Label(text='00:00', parent=self.sr.topParent, left=153, top=12, idx=2, fontsize=10, letterspace=1, uppercase=1)
                else:
                    self.turnCounterText = uicls.Label(text=time, parent=self.sr.topParent, left=183, top=12, idx=2, fontsize=10, letterspace=1, uppercase=1)
                    self.delayCounterText = uicls.Label(text='', parent=self.sr.topParent, left=153, top=12, idx=2, fontsize=10, letterspace=1, uppercase=1)
                blue.pyos.synchro.Sleep(1000)

        except:
            pass



    def MainCounter(self):
        try:
            while self.running:
                self.gameSeconds += 1
                (minutes, seconds,) = self.ToMinutesAndSeconds(self.gameSeconds)
                time = '%s:%s' % (minutes, seconds)
                if not hasattr(self, 'mainCounterText'):
                    return 
                if self.mainCounterText is not None:
                    self.mainCounterText.Close()
                self.mainCounterText = uicls.Label(text=time, parent=self.sr.topParent, left=183, top=2, idx=2, fontsize=10, letterspace=1, uppercase=1)
                blue.pyos.synchro.Sleep(1000)

        except:
            pass



    def ToMinutesAndSeconds(self, totalSeconds):
        if totalSeconds:
            minutes = math.floor(totalSeconds / 60)
            seconds = totalSeconds - minutes * 60
        else:
            minutes = 0
            seconds = 0
        if seconds < 10:
            seconds = '0%d' % int(seconds)
        else:
            seconds = '%d' % int(seconds)
        if minutes < 10:
            minutes = '0%d' % int(minutes)
        else:
            minutes = '%d' % int(minutes)
        return (minutes, seconds)



    def OnTurn(self, *args):
        self.ClearInfo()
        self.controller.EndTurn()



    def OnGiveUp(self, *args):
        ret = eve.Message('CustomQuestion', {'header': mls.UI_MINIGAME_GIVE_UP_CAPTION,
         'question': mls.UI_MINIGAME_GIVE_UP_CONFIRM}, uiconst.YESNO, uiconst.ID_YES)
        if ret == uiconst.ID_YES:
            self.OnClose()



    def OnUndo(self, *args):
        self.controller.Action(slayConst.UNDO, None)



    def OnHelp(self, *args):
        self.controller.ShowHelp()



    def OnConfirmJoin(self, betAmount):
        if betAmount > 0:
            if eve.Message('ConfirmMinigameBet', {'amount': betAmount,
             'game': self.settings.minigameName}, uiconst.OKCANCEL, uiconst.ID_OK) != uiconst.ID_OK:
                return 
        self.controller.ConfirmJoinGame()



    def PerformAction(self, action):
        actions = action.rsplit(' ')
        self.controller.Action(actions[0], actions[1:])



    def AddMessage(self, message, messageType):
        self.lastMessage = message
        if not hasattr(self, 'messageContainer'):
            return 
        if message == '':
            return 
        numLines = 1
        counter = 1
        posIndex = 0
        text = []
        if message == None:
            message = ''
        lines = []
        message = '*%s' % message
        for letter in message:
            if letter == u' ' and counter == 1:
                pass
            else:
                text.append(letter)
            if counter >= 35:
                if letter == u' ':
                    lines.append(text)
                    numLines += 1
                    text = []
                    counter = 0
            counter += 1
            posIndex += 1

        lines.append(text)
        pos = 0
        color = (0.8, 0.9, 0.08, 1.0)
        if messageType == minigameConst.MESSAGE_ERROR:
            color = (1.0, 0.3, 0.1, 1.0)
        elif messageType == minigameConst.MESSAGE_NORMAL:
            color = (0.1, 1.0, 0.2, 1.0)
        indexed = 0
        for text in self.mainMessage:
            text.Close()

        texts = []
        for i in xrange(len(lines) - 1, -1, -1):
            message = ''
            text = lines[i]
            for item in text:
                message += item

            if message[0] != u'*':
                message = ' %s' % message
            texts.insert(0, (message, color))

        self.mainMessage = []
        pos = 0
        for text in texts:
            useText = text[0]
            useColor = text[1]
            if numLines > 0:
                useColor = (1.0, 1.0, 1.0, 1.0)
                numLines -= 1
            textLine = uicls.Label(text=useText, parent=self.messageContainer, color=useColor, left=8, top=pos + 2, idx=2, fontsize=11, letterspace=1, uppercase=0)
            self.mainMessage.append(textLine)
            uthread.new(self.FadeToColor, textLine, text[1])
            pos += 9
            indexed += 1




    def FadeToColor(self, line, finalColor):
        for i in xrange(0, 100, 4):
            diffR = 1.0 - finalColor[0]
            percR = diffR * float(i / 100.0)
            finR = 1.0 - percR
            diffG = 1.0 - finalColor[1]
            percG = diffG * float(i / 100.0)
            finG = 1.0 - percG
            diffB = 1.0 - finalColor[2]
            percB = diffB * float(i / 100.0)
            finB = 1.0 - percB
            line.color.r = finR
            line.color.g = finG
            line.color.b = finB
            line.color.a = 1.0
            blue.pyos.synchro.Sleep(50)




    def CalcColor(self, color, isBanner = False):
        if isBanner:
            colorEnum = slaycommon.ColorEnum()
            if color in colorEnum:
                col = colorEnum[color]
                return util.KeyVal(r=col[0], g=col[1], b=col[2])
            else:
                return util.KeyVal(r=0.0, g=0.0, b=0.0)
        else:
            colEnum = slaycommon.ColorEnum()
            if color in colEnum:
                col = colEnum[color]
                return util.KeyVal(r=col[0], g=col[1], b=col[2])
            else:
                return util.KeyVal(r=0.0, g=0.0, b=0.0)



    def CalcColorHex(self, color):
        color = self.CalcColorSelected(color)
        return trinity.TriColor(color.r, color.g, color.b).AsInt()



    def CalcColorSelected(self, color, isBanner = False):
        color = self.CalcColor(color, isBanner)
        return util.KeyVal(r=color.r * 1.1, g=color.g * 1.1, b=color.b * 1.1)



    def SetBanner(self, playerColor):
        found = False
        for child in self.sr.main.children:
            if child.name == 'banner':
                found = True

        if found == True:
            return 
        banner = draw.TransformContainer('banner', align=uiconst.RELATIVE, width=70, height=70, left=129, top=10, state=uiconst.UI_NORMAL, parent=self.sr.main)
        sm.GetService('info').GetCorpLogo(session.corpid, parent=banner, wnd=self)
        col = self.CalcColorSelected(playerColor, isBanner=True)
        name = cfg.eveowners.Get(session.charid).name
        alphaCol = (col.r,
         col.g,
         col.b,
         1.0)
        uicls.Label(text='%s:' % name, parent=self.sr.main, color=alphaCol, left=129, top=82, idx=2, fontsize=10, letterspace=1, uppercase=0)
        uicls.Label(text=mls.UI_MINIGAME_FACTION % {'name': slaycommon.GetFactionNameByColor(playerColor)}, parent=self.sr.main, color=alphaCol, left=129, top=92, idx=2, fontsize=10, letterspace=1, uppercase=0)



    def ShowInfo(self, economics, units, chartData):
        if hasattr(self, 'infoContainer'):
            self.ClearInfo()
            if economics is not None:
                income = economics.income
                salaries = economics.salaries
                cashFlow = income - salaries
                dspSalaries = '%s%s' % ('-' if salaries > 0 else '', salaries)
                line = 2
                self.infoChildren.append(uicls.Label(text=mls.UI_MINIGAME_INCOME, parent=self.infoContainer, left=4, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                self.infoChildren.append(uicls.Label(text=str(income), parent=self.infoContainer, left=54, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                line += 10
                self.infoChildren.append(uicls.Label(text=mls.UI_MINIGAME_SALARIES, parent=self.infoContainer, left=4, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                self.infoChildren.append(uicls.Label(text=str(dspSalaries), parent=self.infoContainer, left=54, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                line += 10
                self.infoChildren.append(uicls.Label(text=mls.UI_MINIGAME_TOTAL, parent=self.infoContainer, left=4, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                self.infoChildren.append(uicls.Label(text=str(cashFlow), parent=self.infoContainer, left=54, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                line += 10
                self.infoChildren.append(uicls.Label(text='---------------', parent=self.infoContainer, left=4, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                line += 10
                self.infoChildren.append(uicls.Label(text=mls.UI_MINIGAME_SAVED, parent=self.infoContainer, left=4, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                self.infoChildren.append(uicls.Label(text=str(economics.saved), parent=self.infoContainer, left=54, top=line, idx=2, fontsize=10, letterspace=1, uppercase=1))
                unitOffset = 0
                unitColor = (1.0, 1.0, 1.0)
                unitWidth = 58
                unitHeight = 50
                unitName = 'parent_unit'
                for unitID in units:
                    imageFile = self.GetRes(unitID)
                    if units[unitID] > 0:
                        container = minigames.MinigameDraggable(name=unitName, align=uiconst.BOTTOMLEFT, state=uiconst.UI_NORMAL, parent=self.infoContainer)
                        container.height = unitHeight
                        container.width = unitWidth
                        container.gameGui = self
                        unitName = 'peasant'
                        i = 0
                        if unitID != slayConst.OCCUPY_PEASANT:
                            unitName = 'castle'
                        quantityLabel = uicls.Label(text='', parent=container, left=4, align=uiconst.TOPLEFT, letterspace=1, fontsize=9, idx=0, singleline=1)
                        quantityLabel.state = uiconst.UI_DISABLED
                        quantityLabel.top = -4
                        quantityLabel.left = 4 + unitOffset
                        quantityLabel.text = str(units[unitID])
                        data = {'x': -1,
                         'y': -1,
                         'candrag': True,
                         'icon': imageFile,
                         'unitID': unitID}
                        container.data = data
                        sprite = uicls.Sprite(name='_new_%s' % i, parent=container, texturePath=imageFile, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, color=unitColor)
                        sprite.top = -4
                        sprite.left = 4
                        sprite.width = unitWidth
                        sprite.height = unitHeight
                        self.infoChildren.append(container)
                        container.left = unitOffset
                    unitOffset = unitOffset + 60

            owners = {}
            totalTiles = 0
            if self.storedTableData is not None:
                for key in self.storedTableData:
                    rawTile = self.storedTableData[key]
                    if rawTile != None:
                        tile = slaycommon.SlayTile()
                        tile.FromRaw(rawTile)
                        totalTiles += 1
                        if tile.owner in owners:
                            owners[tile.owner][0] += 1
                        elif tile.owner is not None:
                            owners[tile.owner] = [1, tile.color]




    def MergeColors(self, playerColor, pixel2):
        return pixel2
        pixel1 = self.CalcColorHex(playerColor)
        return pixel1



    def MakeGraphEntryDict(self, gameStatusEntry):
        entries = {}
        for player in gameStatusEntry:
            entries[player.name] = util.KeyVal(points=player.points, color=player.color)

        return entries



    def GetChart(self, chartData):
        if self.lastChartData is not None and len(chartData[0]) > 0 and len(chartData) == len(self.lastChartData):
            return 
        if len(chartData[0]) == 0:
            return 
        self.lastChartData = copy.deepcopy(chartData)
        if hasattr(self, 'playerInfoContainer'):
            self.playerInfoContainer.Close()
        self.playerInfoContainer = uicls.Container(name='playerInfoContainer', align=uiconst.RELATIVE, width=200, height=168, left=5, top=160, state=uiconst.UI_NORMAL, parent=self.sr.main)
        uicls.Frame(parent=self.playerInfoContainer)
        c = XYChart(self.playerInfoContainer.width, self.playerInfoContainer.height, Transparent)
        c.setColors(whiteOnBlackPalette)
        c.setBackground(Transparent)
        c.setTransparentColor(-1)
        c.setAntiAlias(1, 1)
        (fontFace, fontSize,) = ('simsun.ttc', 7)
        axis = c.yAxis()
        axis.setLabelStyle(fontFace, fontSize)
        axis.setAutoScale(0.1, 0.1, 0.3)
        skips = 1
        counter = 1
        for i in xrange(len(chartData)):
            if counter >= 10:
                counter = 0
                skips += 1
            counter += 1

        if skips >= 2:
            c.xAxis().setLabelStep(skips)
        labels = []
        cnt = 1
        for item in chartData:
            labels.append(str(cnt))
            cnt += 1

        c.xAxis().setLabels2(labels)
        c.xAxis().setLabelStyle(fontFace, fontSize)
        if skips >= 2:
            c.xAxis().setLabelStep(skips, 2, 10)
        c.setPlotArea(25, 5, self.playerInfoContainer.width - 30, self.playerInfoContainer.height - 30, -1, -1, -1, -1)
        c.addLegend(105, 18, 0, fontFace, fontSize).setBackground(Transparent)
        lineLayers = []
        playerGraph = {}
        playerColors = {}
        for player in chartData[0]:
            playerGraph[player.name] = []
            playerColors[player.name] = player.color

        for playerName in playerGraph:
            line = []
            for gameStatusEntry in chartData:
                entryDict = self.MakeGraphEntryDict(gameStatusEntry)
                if playerName not in entryDict:
                    line.append(0)
                else:
                    line.append(entryDict[playerName].points)

            line.append(playerColors[playerName])
            lineLayers.append(line)

        for playerData in lineLayers:
            col = playerData[(len(playerData) - 1)]
            playerData.remove(col)
            color = self.CalcColorHex(col)
            lineLayer = c.addLineLayer(playerData, color)
            if len(chartData) == 1:
                lineLayer.getDataSet(0).setDataSymbol(SquareSymbol, 5, fillColor=color, edgeColor=color)

        lf = '{value}'
        c.yAxis().setLabelFormat(lf)
        c.layout()
        self.chart = trinity.device.CreateOffscreenPlainSurface(self.playerInfoContainer.width, self.playerInfoContainer.height, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        self.chart.LoadSurfaceFromFileInMemory(c.makeChart2(PNG))
        linegr = uicls.Sprite(name='chart', parent=self.playerInfoContainer, align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0))
        linegr.texture.atlasTexture = uicore.uilib.CreateTexture(width, height)
        linegr.texture.atlasTexture.CopyFromSurface(surface)



    def ClearInfo(self):
        toDel = []
        for child in self.infoContainer.children:
            if child.name != 'frame':
                toDel.append(child)

        for child in toDel:
            self.infoContainer.children.remove(child)

        self.infoChildren = []



    def OnDropNodes(self, fromNodes, toNode):
        self.slayCamera.freeze = False
        sourceData = fromNodes[0].data
        targetData = toNode.data
        if sourceData['x'] == -1:
            self.controller.AddUnit(targetData['x'], targetData['y'], sourceData['unitID'])
        else:
            self.controller.MoveUnit(sourceData['x'], sourceData['y'], targetData['x'], targetData['y'])



    def GetRes(self, unitType):
        if unitType == slayConst.OCCUPY_PEASANT:
            return 'res:/Graphics/Placeable/Minigames/Slay/Unit_Peasant128.png'
        else:
            if unitType == slayConst.OCCUPY_SPEARMAN:
                return 'res:/Graphics/Placeable/Minigames/Slay/Unit_Spearman128.png'
            if unitType == slayConst.OCCUPY_CASTLE:
                return 'res:/Graphics/Placeable/Minigames/Slay/Unit_Castle128.png'
            if unitType == slayConst.OCCUPY_KNIGHT:
                return 'res:/Graphics/Placeable/Minigames/Slay/Unit_Knight128.png'
            if unitType == slayConst.OCCUPY_BARON:
                return 'res:/Graphics/Placeable/Minigames/Slay/Unit_Baron128.png'
            return ''




