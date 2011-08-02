import math
import util
import uicls
import uiutil
import uiconst

class SlayRunningBetGUI(uicls.Window):
    __guid__ = 'minigames.SlayRunningBetGUI'
    default_width = 255
    default_height = 170

    def SetConfig(self, maxBetAmount, playerPoints, controller):
        self.playerPoints = playerPoints
        self.maxBetAmount = maxBetAmount
        self.controller = controller
        self.sr.main = uiutil.GetChild(self, 'main')
        uicls.Line(align=uiconst.TOTOP, parent=self.sr.main)
        line = -38
        uicls.Label(text=mls.UI_MINIGAME_RUNNING_BET_CAPTION, parent=self.sr.main, left=70, top=line, idx=2, fontsize=24, letterspace=1, uppercase=1)
        line += 48
        uicls.Label(text=mls.UI_RUNNING_BET_LIMIT % util.FmtISK(maxBetAmount), parent=self.sr.main, left=10, top=10, idx=2, fontsize=11, letterspace=1, uppercase=0)
        line += 15
        self.pointCommittment = uicls.Label(text=mls.UI_MINIGAME_RUNNING_BET_POINT_COST % {'points': str(playerPoints)}, parent=self.sr.main, left=10, top=line, idx=2, fontsize=11, letterspace=1, uppercase=0)
        line += 35
        self.betAmount = uicls.EditPlainText(name='betAmount', readonly=False, parent=self.sr.main, align=uiconst.RELATIVE, pos=(10,
         line,
         self.width - 20,
         25), padding=(0, 0, 0, 0))
        self.betAmount.OnChange = self.BetAmountChange
        line += 30
        sb = uicls.Button(parent=self.sr.main, label=mls.UI_CMD_SUBMIT, func=self.OnSubmit, left=7, top=line)
        uicls.Button(parent=self.sr.main, label=mls.UI_CMD_CANCEL, func=self.OnCancel, left=sb.left + sb.width + 2, top=line)
        xPos = int(uicore.desktop.width / 2 - self.width / 2)
        yPos = int(uicore.desktop.height / 2 - self.height / 2)
        self.SetPosition(xPos, yPos)
        self.SetWndIcon('40_14')
        self.SetCaption(mls.UI_MINIGAME_RUNNING_BET_DEFINE_CAPTION)



    def BetAmountChange(self, *args):
        try:
            amount = int(self.betAmount.GetValue())
            percOfTotal = float(amount) / float(self.maxBetAmount)
            numPoints = int(math.ceil(percOfTotal * float(self.playerPoints)))
            percDisplay = str(round(percOfTotal * 100, 2))
            if percOfTotal == 0:
                percDisplay = '0'
            elif percOfTotal < 0.01:
                percDisplay = '0..'
            if numPoints > self.playerPoints:
                self.pointCommittment.SetText(mls.UI_MINIGAME_RUNNING_BET_INVALID_INPUT)
            else:
                self.pointCommittment.SetText(mls.UI_MINIGAME_RUNNING_BET_GAME_POINT_COST % {'amount': str(numPoints),
                 'points1': str(percDisplay),
                 'points2': self.playerPoints})
        except:
            self.pointCommittment.SetText(mls.UI_MINIGAME_RUNNING_BET_INVALID_INPUT)



    def OnSubmit(self, *args):
        try:
            amount = int(self.betAmount.GetValue())
            if amount > self.maxBetAmount:
                sm.StartService('gameui').MessageBox(mls.UI_MINIGAME_RUNNING_BET_CANT_BET_THAT_MUCH % {'amount': util.FmtISK(amount)}, mls.UI_MINIGAME_INPUT_ERROR_CAPTION)
            elif amount < 1:
                sm.StartService('gameui').MessageBox(mls.UI_MINIGAME_RUNNING_BET_MIN_BET % {'amount': util.FmtISK(1)}, mls.UI_MINIGAME_INPUT_ERROR_CAPTION)
            self.controller.SubmitRunningBet(amount)
            self.controller = None
            self.Close()
        except:
            sm.StartService('gameui').MessageBox(mls.UI_MINIGAME_RUNNING_BET_INPUT_NOT_NUMBER, mls.UI_MINIGAME_INPUT_ERROR_CAPTION)



    def OnCancel(self, *args):
        self.controller.CancelRunningBet()
        self.controller = None
        self.Close()



    def OnClose(self, *args):
        if self.controller:
            self.controller.CancelRunningBet()




