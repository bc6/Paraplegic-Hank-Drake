import uthread
import draw
import weakref
import uiutil
import uiconst
import log
import uicls

class SinglelineEdit(uicls.SinglelineEditCore):
    __guid__ = 'uicls.SinglelineEdit'
    default_left = 0
    default_top = 2
    default_width = 80
    default_height = 18
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        self.registerHistory = True
        self.adjustWidth = False
        self.sr.combo = None
        self.label = ''
        uicls.SinglelineEditCore.ApplyAttributes(self, attributes)
        self.displayHistory = True
        if self.GetAlign() == uiconst.TOALL:
            self.height = 0
        else:
            self.height = self.default_height



    def Prepare_(self):
        self.sr.text = uicls.Label(text='', parent=self.sr.content, left=self.TEXTLEFTMARGIN, top=1, state=uiconst.UI_DISABLED, singleline=1)
        self.sr.hinttext = uicls.Label(text='', parent=self.sr.content, name='hinttext', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, singleline=True, left=self.TEXTLEFTMARGIN, autowidth=True, autoheight=True)
        self.sr.background = uicls.Container(name='_underlay', parent=self, state=uiconst.UI_DISABLED)
        self.sr.backgroundFrame = uicls.BumpedUnderlay(parent=self.sr.background)
        sm.GetService('window').CheckControlAppearance(self)
        self.sr.content.clipChildren = 1
        self.sr.content.SetPadding(1, 1, 1, 1)
        self.Prepare_ActiveFrame_()



    def SetLabel(self, text):
        self.sr.label = uicls.Label(parent=self, name='__caption', text=text, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, idx=0, top=-13, uppercase=1, fontsize=10, letterspace=1, linespace=9)
        if self.adjustWidth:
            self.width = max(self.width, self.sr.label.textwidth)



    def LoadCombo(self, id, options, callback = None, setvalue = None, comboIsTabStop = 1):
        for each in self.children:
            if each.name == 'combo':
                each.Close()

        combo = uicls.Combo(parent=self, label='', options=options, name=id, select=setvalue, callback=self.OnComboChange, pos=(0, 0, 0, 0), width=15, align=uiconst.TORIGHT, idx=0)
        combo.sr.inputCallback = callback
        combo.isTabStop = comboIsTabStop
        combo.name = 'combo'
        combo.Confirm = self.ComboConfirm
        combo.HideText()
        self.sr.content.width = 2
        self.sr.background.width = 2
        self.sr.activeframe.width = 2
        self.sr.combo = combo



    def ComboConfirm(self, *args):
        if self.sr.combo and not self.sr.combo.destroyed:
            self.OnComboChange(self.sr.combo, self.sr.combo.GetKey(), self.sr.combo.GetValue())
        self.sr.combo.Cleanup(setfocus=0)



    def OnUp(self, *args):
        if self.sr.combo:
            self.sr.combo.OnUp()



    def OnDown(self, *args):
        if self.sr.combo:
            self.sr.combo.OnDown()



    def GetComboValue(self):
        if self.sr.combo:
            return self.sr.combo.GetValue()



    def OnComboChange(self, combo, label, value, *args):
        self.SetValue(label, updateIndex=0)
        if combo.sr.inputCallback:
            combo.sr.inputCallback(combo, label, value)



    def ClearHistory(self, *args):
        (id, mine, all,) = self.GetHistory(getAll=1)
        if id in all:
            del all[id]
            settings.user.ui.Set('editHistory', all)



    def RegisterHistory(self, value = None):
        if self.integermode or self.floatmode or self.passwordchar is not None or not self.registerHistory:
            return 
        (id, mine, all,) = self.GetHistory(getAll=1)
        current = (value or self.GetValue(registerHistory=0)).rstrip()
        if current not in mine:
            mine.append(current)
        all[id] = mine
        settings.user.ui.Set('editHistory', all)



    def CheckHistory(self):
        if self.integermode or self.floatmode or self.passwordchar is not None or self.displayHistory == 0:
            return 
        if self.readonly:
            return 
        valid = self.GetValid()
        if valid:
            self.ShowHistoryMenu(valid[:5])
            return 1
        self.CloseHistoryMenu()
        return 0



    def GetValid(self):
        current = self.GetValue(registerHistory=0)
        (id, mine,) = self.GetHistory()
        valid = [ each for each in mine if each.lower().startswith(current.lower()) if each != current ]
        valid = uiutil.SortListOfTuples([ (len(each), each) for each in valid ])
        return valid



    def ShowHistoryMenu(self, history):
        hadMenu = 0
        if self.historyMenu and self.historyMenu():
            hadMenu = 1
        self.CloseHistoryMenu()
        if not history:
            return 
        (l, t, w, h,) = self.GetAbsolute()
        mp = uicls.Container(name='historyMenuParent', parent=uicore.layer.menu, pos=(l,
         t + h + 2,
         w,
         0), align=uiconst.TOPLEFT)
        if not hadMenu:
            mp.opacity = 0.0
        uicls.Frame(parent=mp, frameConst=uiconst.FRAME_BORDER1_CORNER0, color=(1.0, 1.0, 1.0, 0.2))
        uicls.Frame(parent=mp, frameConst=uiconst.FRAME_FILLED_CORNER0, color=(0.0, 0.0, 0.0, 0.75))
        mps = uicls.Container(name='historyMenuSub', parent=mp, idx=0)
        self.PopulateHistoryMenu(mps, mp, history)
        mp.sr.entries = mps
        self.historyMenu = weakref.ref(mp)
        if not hadMenu:
            uicore.effect.MorphUI(mp, 'opacity', 1.0, 250.0, float=1)



    def PopulateHistoryMenu(self, mps, mp, history):
        history.sort()
        current = self.GetValue(registerHistory=0)
        if current:
            valid = [current] + history
        else:
            valid = history
        ep = None
        for h in valid:
            self.GetHistoryMenuEntry(h, h, mps, mp)

        if ep:
            ep.children.remove(ep.children[0])



    def GetHistoryMenuEntry(self, displayText, text, menuSub, mp, info = None):
        ep = uicls.Container(name='entryParent', parent=menuSub, clipChildren=1, pos=(0, 0, 0, 16), align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        ep.OnMouseEnter = (self.HEMouseEnter, ep)
        ep.OnMouseDown = (self.HEMouseDown, ep)
        ep.OnMouseUp = (self.HEMouseUp, ep)
        uicls.Line(parent=ep, align=uiconst.TOBOTTOM)
        t = uicls.Label(text=displayText, parent=ep, left=6, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        ep.height = t.textheight + 4
        ep.sr.hilite = uicls.Fill(parent=ep, color=(1.0, 1.0, 1.0, 0.25), pos=(1, 1, 1, 1), state=uiconst.UI_HIDDEN)
        ep.selected = 0
        ep.sr.menu = mp
        ep.string = text
        mp.height += ep.height
        ep.info = info



    def HEMouseDown(self, entry, *args):
        self.SetValue(entry.string, updateIndex=1)
        self.OnHistoryClick(entry.string)



    def HEMouseUp(self, entry, *args):
        self.CloseHistoryMenu()



    def GetHistory(self, getAll = 0):
        id = self.GetHistoryID()
        all = settings.user.ui.Get('editHistory', {})
        if type(all) == list:
            log.LogError('Singlelineedit error: all:', all)
            log.LogTraceback('Singlelineedit error: all: %s' % all, severity=log.LGERR)
            settings.user.ui.Delete('editHistory')
            all = {}
        if getAll:
            return (id, all.get(id, []), all)
        return (id, all.get(id, []))



    def OnHistoryClick(self, clickedString, *args):
        pass




