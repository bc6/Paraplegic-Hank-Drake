#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/login/charcreation/historySlider.py
import uiconst
import uicls
import uthread
import uiutil
import base
import ccConst
import localization

class CharacterCreationHistorySlider(uicls.Container):
    __guid__ = 'uicls.CharacterCreationHistorySlider'
    __notifyevents__ = ['OnDollUpdated', 'OnHistoryUpdated']
    SIZE = 20
    BITWIDTH = 4
    BITGAP = 3
    default_name = 'CharacterCreationHistorySlider'
    default_left = 0
    default_top = 0
    default_width = 400
    default_height = SIZE
    default_align = uiconst.CENTER

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        if not attributes.parent:
            uicore.layer.main.children.insert(0, self)
        self.bitChangeCheck = attributes.bitChangeCheck
        self._lastLit = None
        self._currentIndex = None
        self._scrolling = False
        self._mouseOffset = 0
        self._lastLoadIndex = attributes.lastLitHistoryBit
        for name, icon, align in (('left', ccConst.ICON_BACK, uiconst.TOLEFT), ('right', ccConst.ICON_NEXT, uiconst.TORIGHT)):
            btn = uicls.Container(name='%sBtn' % name, parent=self, align=align, width=self.SIZE, state=uiconst.UI_NORMAL)
            btn.sr.icon = uicls.Icon(name='%sIcon' % name, icon=icon, parent=btn, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
            uicls.Frame(parent=btn, frameConst=ccConst.MAINFRAME_INV)
            uicls.Fill(parent=btn, color=(0.0, 0.0, 0.0, 0.25))
            btn.OnClick = (self.OnButtonClicked, btn)
            btn.OnMouseEnter = (self.OnButtonEnter, btn)
            btn.OnMouseExit = (self.OnButtonExit, btn)
            btn.cursor = uiconst.UICURSOR_SELECT

        uicls.CCLabel(parent=self, idx=0, text=localization.GetByLabel('UI/Login/CharacterCreation/UndoHistory'), top=-16, uppercase=True, letterspace=1, shadowOffset=(0, 0), color=ccConst.COLOR50)
        self.sr.mainPar = uicls.Container(parent=self, clipChildren=True, padding=(3, 0, 3, 0))
        self.sr.bitParent = uicls.Container(parent=self.sr.mainPar, align=uiconst.TOPLEFT, height=self.SIZE)
        self.sr.scrollHandle = uicls.Container(parent=self.sr.bitParent, align=uiconst.TOPLEFT, pos=(0,
         0,
         10,
         self.SIZE), color=(1.0, 1.0, 1.0, 1.0), state=uiconst.UI_NORMAL)
        uicls.Fill(parent=self.sr.scrollHandle, color=(1.0, 1.0, 1.0, 1.0), padding=(2, 0, 2, 0))
        self.sr.scrollHandle.OnMouseDown = self.SH_MouseDown
        self.sr.scrollHandle.OnMouseUp = self.SH_MouseUp
        uicls.Frame(parent=self.sr.mainPar, frameConst=ccConst.MAINFRAME_INV)
        uicls.Fill(parent=self.sr.mainPar, color=(0.0, 0.0, 0.0, 0.25))
        frame = uicls.Frame(parent=self, frameConst=ccConst.FRAME_SOFTSHADE, color=(0.0, 0.0, 0.0, 0.25))
        frame.padding = (-32, -5, -32, -15)
        self.UpdateHistory()
        sm.RegisterNotify(self)

    def OnDollUpdated(self, charID, redundantUpdate, *args):
        if not self.destroyed and not redundantUpdate and self.state != uiconst.UI_HIDDEN:
            self.UpdateHistory()

    def OnHistoryUpdated(self, *args):
        if not self.destroyed:
            self.UpdateHistory()

    def UpdateHistory(self):
        dnaLog = uicore.layer.charactercreation.GetDollDNAHistory()
        if dnaLog is not None:
            self.LoadHistory(len(dnaLog))

    def GetCurrentIndexAndMaxIndex(self):
        if self._lastLit and self._lastLit in self.sr.bitParent.children:
            currentIndex = self.sr.bitParent.children.index(self._lastLit) - 1
        else:
            currentIndex = 0
        return (currentIndex, len(self.sr.bitParent.children) - 2)

    def OnButtonClicked(self, button, *args):
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        if button.name == 'leftBtn':
            direction = -1
        else:
            direction = 1
        self.ButtonScroll(direction)

    def ButtonScroll(self, direction):
        currentIndex, maxIndex = self.GetCurrentIndexAndMaxIndex()
        if currentIndex + direction > maxIndex:
            return
        currentIndex += 1
        newIndex = max(0, min(len(self.sr.bitParent.children) - 1, direction + currentIndex))
        if newIndex == 0:
            self._lastLit = None
        else:
            self._lastLit = self.sr.bitParent.children[newIndex]
        self.SettleScrollHandle()
        self.UpdateBitsState()
        self.UpdatePosition()

    def OnButtonEnter(self, button, *args):
        button.sr.icon.SetAlpha(1.0)

    def OnButtonExit(self, button, *args):
        button.sr.icon.SetAlpha(0.5)

    def LoadHistory(self, historyLength):
        uiutil.FlushList(self.sr.bitParent.children[1:])
        litBit = None
        for i in xrange(historyLength):
            bit = uicls.Container(parent=self.sr.bitParent, name='bit_%s' % i, align=uiconst.TOPLEFT, pos=(i * (self.BITWIDTH + self.BITGAP),
             0,
             self.BITWIDTH + self.BITGAP,
             self.SIZE), state=uiconst.UI_NORMAL)
            uicls.Fill(parent=bit, color=(1.0, 1.0, 1.0, 0.75), padding=(self.BITGAP,
             4,
             0,
             4))
            bit.OnClick = (self.OnClickBit, bit)
            bit.idx = i
            if i == self._lastLoadIndex:
                litBit = bit

        self._lastLoadIndex = None
        self.UpdateContentWidth()
        if litBit is None:
            self.ScrollTo(1.0, initing=True)
        else:
            self._lastLit = litBit
            self.SettleScrollHandle(initing=True)
            self.UpdateBitsState()

    def OnClickBit(self, bit, *args):
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        self._lastLit = bit
        self.SettleScrollHandle()
        self.UpdateBitsState()

    def UpdateContentWidth(self):
        self.sr.bitParent.width = (len(self.sr.bitParent.children) - 1) * (self.BITWIDTH + self.BITGAP) + self.BITGAP

    def ScrollTo(self, portion, initing = False):
        l, t, w, h = self.sr.mainPar.GetAbsolute()
        scrollRange = min(0, w - self.sr.bitParent.width)
        self.sr.scrollHandle.left = int((self.sr.bitParent.width - self.sr.scrollHandle.width) * portion)
        self.UpdatePosition()
        self.SettleScrollHandle(initing)

    def SH_MouseDown(self, *args):
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        l, t, w, h = self.sr.scrollHandle.GetAbsolute()
        self._mouseOffset = uicore.uilib.x - l
        self._scrolling = True
        self.sr.scrollTimer = base.AutoTimer(5, self.DragScroll)

    def SH_MouseUp(self, *args):
        if self.bitChangeCheck and not self.bitChangeCheck():
            return
        self._scrolling = False
        self._mouseOffset = 0
        self.sr.scrollTimer = None
        self.SettleScrollHandle()

    def SettleScrollHandle(self, initing = False):
        if self._lastLit is not None:
            self.sr.scrollHandle.left = self._lastLit.left
            if not initing:
                self._currentIndex = self._lastLit.idx
                uthread.new(uicore.layer.charactercreation.LoadDnaFromHistory, self._lastLit.idx)
                self._lastLoadIndex = self._lastLit.idx
        else:
            self.sr.scrollHandle.left = -2

    def DragScroll(self, *args):
        l, t, w, h = self.sr.mainPar.GetAbsolute()
        bl, bt, bw, bh = self.sr.bitParent.GetAbsolute()
        self.sr.scrollHandle.left = min(bw - self.sr.scrollHandle.width, max(0, uicore.uilib.x - self._mouseOffset - bl))
        self.UpdatePosition()

    def UpdatePosition(self):
        l, t, w, h = self.sr.mainPar.GetAbsolute()
        sl, st, sw, sh = self.sr.scrollHandle.GetAbsolute()
        if self.sr.bitParent.width <= w:
            self.sr.bitParent.left = 0
        elif sl < l:
            self.sr.bitParent.left += l - sl
        elif sl + sw > l + w:
            self.sr.bitParent.left -= sl + sw - (l + w)
        self.UpdateBitsState()

    def UpdateBitsState(self):
        self._lastLit = None
        l, t, w, h = self.sr.bitParent.GetAbsolute()
        for bit in self.sr.bitParent.children[1:]:
            if bit.left + self.BITGAP + self.BITWIDTH / 2 > self.sr.scrollHandle.left + self.sr.scrollHandle.width / 2:
                bit.children[0].color.a = 0.25
            else:
                bit.children[0].color.a = 1.0
                self._lastLit = bit