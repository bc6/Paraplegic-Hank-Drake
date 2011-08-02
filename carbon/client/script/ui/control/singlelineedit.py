import uthread
import blue
import base
import sys
import types
import weakref
import util
import fontConst
import uiconst
import uiutil
import uicls

class SinglelineEditCore(uicls.Area):
    __guid__ = 'uicls.SinglelineEditCore'
    default_name = 'edit_singleline'
    default_align = uiconst.TOTOP
    default_width = 100
    default_height = 20
    default_state = uiconst.UI_NORMAL
    default_maxLength = None
    default_label = ''
    default_setvalue = ''
    default_hinttext = ''
    default_passwordCharacter = None
    default_autoselect = False
    default_adjustWidth = False
    default_OnChange = None
    default_OnFocusLost = None
    default_OnReturn = None
    default_OnAnyChar = None
    default_OnInsert = None
    TEXTLEFTMARGIN = 6
    TEXTRIGHTMARGIN = 4
    DECIMAL = prefs.GetValue('decimal', '.')
    DIGIT = prefs.GetValue('digit', ',')

    def ApplyAttributes(self, attributes):
        uicls.Area.ApplyAttributes(self, attributes)
        self.hinttext = ''
        self.isTabStop = 1
        self.integermode = None
        self.floatmode = None
        self.passwordchar = None
        self.caretIndex = (0, 0)
        self.selFrom = None
        self.selTo = None
        self.value = None
        self.text = ''
        self.suffix = ''
        self.maxletters = None
        self.historyMenu = None
        self.historySaveLast = None
        self.readonly = False
        self.displayHistory = False
        self.allowHistoryInnerMatches = False
        self.maxHistoryShown = 5
        self.OnChange = None
        self.OnFocusLost = None
        self.OnReturn = None
        self.OnInsert = None
        self.Prepare_()
        self.autoselect = attributes.get('autoselect', self.default_autoselect)
        self.font = attributes.get('font', fontConst.DEFAULT_FONT)
        self.fontsize = attributes.get('fontsize', fontConst.DEFAULT_FONTSIZE)
        self.adjustWidth = attributes.get('adjustWidth', self.default_adjustWidth)
        self.sr.text.font = self.sr.hinttext.font = attributes.get('font', fontConst.DEFAULT_FONT)
        self.sr.text.fontsize = self.sr.hinttext.fontsize = attributes.get('fontsize', fontConst.DEFAULT_FONTSIZE)
        self.sr.text.shadow = self.sr.hinttext.shadow = attributes.get('shadow', None)
        fontcolor = attributes.get('fontcolor', (1.0, 1.0, 1.0, 1.0))
        if fontcolor is not None:
            self.SetTextColor(fontcolor)
        if attributes.get('ints', None):
            self.IntMode(*attributes.ints)
        elif attributes.get('floats', None):
            self.FloatMode(*attributes.floats)
        self.SetPasswordChar(attributes.get('passwordCharacter', self.default_passwordCharacter))
        self.SetMaxLength(attributes.get('maxLength', self.default_maxLength))
        self.SetLabel(attributes.get('label', self.default_label))
        self.SetValue(attributes.get('setvalue', self.default_setvalue))
        self.SetHintText(attributes.get('hinttext', self.default_hinttext))
        self.height = 20
        self.OnChange = attributes.get('OnChange', self.default_OnChange)
        self.OnFocusLost = attributes.get('OnFocusLost', self.default_OnFocusLost)
        self.OnReturn = attributes.get('OnReturn', self.default_OnReturn)
        self.OnInsert = attributes.get('OnInsert', self.default_OnInsert)
        OnAnyChar = attributes.get('OnAnyChar', self.default_OnAnyChar)
        if OnAnyChar:
            self.OnAnyChar = OnAnyChar



    def Prepare_(self):
        self.Prepare_Background_()
        self.sr.text = uicls.Label(text='', parent=self.sr.content, name='value', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, singleline=True, left=self.TEXTLEFTMARGIN)
        self.sr.hinttext = uicls.Label(text='', parent=self.sr.content, name='hinttext', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, singleline=True, left=self.TEXTLEFTMARGIN)
        self.sr.content.clipChildren = 1
        self.sr.content.SetPadding(1, 1, 1, 1)
        self.Prepare_ActiveFrame_()



    def SetHintText(self, hint):
        self.hinttext = hint
        self.CheckHintText()



    def CheckHintText(self):
        if self.hinttext and not self.GetText():
            self.sr.hinttext.text = self.hinttext
        else:
            self.sr.hinttext.text = ''



    def SetTextColor(self, color):
        self.sr.text.SetRGB(*color)
        self.sr.hinttext.SetRGB(*color)
        self.sr.hinttext.SetAlpha(self.sr.hinttext.GetAlpha() * 0.5)



    def Prepare_Background_(self):
        self.LoadUnderlay(color=(0.0, 0.0, 0.0, 0.5))



    def Prepare_ActiveFrame_(self):
        self.sr.activeframe = uicls.Frame(name='__activeframe', parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=1, color=(1.0, 1.0, 1.0, 0.75))



    def Prepare_Caret_(self):
        (l, t, w, h,) = self.GetAbsolute()
        self.sr.caret = uicls.Fill(parent=self.sr.content, name='caret', align=uiconst.TOPLEFT, color=(1.0, 1.0, 1.0, 0.75), pos=(self.TEXTLEFTMARGIN,
         1,
         1,
         h - 2), idx=0, state=uiconst.UI_HIDDEN)



    def _OnResize(self, *args, **kw):
        uthread.new(self._SinglelineEditCore__OnResize, *args, **kw)



    def __OnResize(self, *args, **kw):
        uicls.Area._OnResize(self, *args, **kw)
        (l, t, w, h,) = self.GetAbsolute()
        if w > 1:
            self.RefreshCaretPosition()
            self.RefreshSelectionDisplay()



    def ClearHistory(self, *args):
        (id, mine, all,) = self.GetHistory(getAll=1)
        if id in all:
            del all[id]
            settings.public.generic.Set('editHistory', all)



    def RegisterHistory(self, value = None):
        if self.integermode or self.floatmode or self.passwordchar is not None:
            return 
        (id, mine, all,) = self.GetHistory(getAll=1)
        current = (value or self.GetValue(registerHistory=0)).rstrip()
        if current not in mine:
            mine.append(current)
        all[id] = mine
        settings.public.generic.Set('editHistory', all)



    def CheckHistory(self):
        if self.integermode or self.floatmode or self.passwordchar is not None or self.displayHistory == 0:
            return 
        if self.readonly:
            return 
        current = self.GetValue(registerHistory=0)
        (id, mine,) = self.GetHistory()
        if self.allowHistoryInnerMatches:
            valid = [ each for each in mine if current.lower() in each.lower() if each != current ]
        else:
            valid = [ each for each in mine if each.lower().startswith(current.lower()) if each != current ]
        valid = uiutil.SortListOfTuples([ (len(each), each) for each in valid ])
        if valid:
            self.ShowHistoryMenu(valid[:self.maxHistoryShown])
            return 1
        self.CloseHistoryMenu()
        return 0



    def ShowHistoryMenu(self, history):
        hadMenu = 0
        if self.historyMenu and self.historyMenu():
            hadMenu = 1
        self.CloseHistoryMenu()
        if not history:
            return 
        (l, t, w, h,) = self.GetAbsolute()
        menuParent = uicls.Container(name='historyMenuParent', parent=uicore.layer.menu, align=uiconst.TOPLEFT, pos=(l,
         t + h + 2,
         w,
         0))
        mps = uicls.Container(name='historyMenuSub', parent=menuParent)
        uicls.Frame(parent=menuParent, frameConst=uiconst.FRAME_BORDER1_CORNER0, color=(1.0, 1.0, 1.0, 0.2))
        uicls.Frame(parent=menuParent, frameConst=uiconst.FRAME_FILLED_CORNER0, color=(0.0, 0.0, 0.0, 0.75))
        if not hadMenu:
            menuParent.opacity = 0.0
        history.sort()
        current = self.GetValue(registerHistory=0)
        if current:
            valid = [current] + history
        else:
            valid = history
        ep = None
        for h in valid:
            ep = uicls.Container(name='entryParent', parent=mps, align=uiconst.TOTOP, pos=(0, 0, 0, 16), clipChildren=1, state=uiconst.UI_NORMAL)
            ep.OnMouseEnter = (self.HEMouseEnter, ep)
            ep.OnMouseDown = (self.HEMouseDown, ep)
            uicls.Line(parent=ep, align=uiconst.TOBOTTOM)
            t = uicls.Label(text=h, parent=ep, pos=(6, 0, 0, 0), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
            ep.height = t.textheight + 4
            ep.sr.hilite = uicls.Fill(parent=ep, color=(1.0, 1.0, 1.0, 0.25), pos=(1, 1, 1, 1), state=uiconst.UI_HIDDEN)
            ep.selected = 0
            ep.sr.menu = menuParent
            ep.string = h
            menuParent.height += ep.height

        if ep:
            ep.children.remove(ep.children[0])
        menuParent.sr.entries = mps
        self.historyMenu = weakref.ref(menuParent)
        if not hadMenu:
            uicore.effect.MorphUI(menuParent, 'opacity', 1.0, 250.0, float=1)



    def HEMouseEnter(self, entry, *args):
        if not (self.historyMenu and self.historyMenu()):
            return 
        hm = self.historyMenu()
        for _entry in hm.sr.entries.children:
            _entry.sr.hilite.state = uiconst.UI_HIDDEN
            _entry.selected = 0

        entry.sr.hilite.state = uiconst.UI_DISABLED
        entry.selected = 1



    def HEMouseDown(self, entry, *args):
        self.SetValue(entry.string, updateIndex=1)



    def CloseHistoryMenu(self):
        if not (self.historyMenu and self.historyMenu()):
            return 
        import menu
        self.active = None
        menu.KillAllMenus()
        self.historyMenu = None



    def BrowseHistory(self, down):
        justopened = 0
        if not (self.historyMenu and self.historyMenu()):
            if not self.CheckHistory():
                return 
            justopened = 1
        hm = self.historyMenu()
        currentIdx = None
        i = 0
        for entry in hm.sr.entries.children:
            if entry.selected:
                currentIdx = i
            entry.sr.hilite.state = uiconst.UI_HIDDEN
            entry.selected = 0
            i += 1

        if justopened:
            return 
        if currentIdx is None:
            if down:
                currentIdx = 0
            else:
                currentIdx = len(hm.sr.entries.children) - 1
        elif down:
            currentIdx += 1
            if currentIdx >= len(hm.sr.entries.children):
                currentIdx = 0
        else:
            currentIdx -= 1
            if currentIdx < 0:
                currentIdx = len(hm.sr.entries.children) - 1
        self.active = active = hm.sr.entries.children[currentIdx]
        active.sr.hilite.state = uiconst.UI_DISABLED
        active.selected = 1
        if not getattr(self, 'blockSetValue', 0):
            self.SetValue(active.string, updateIndex=1)



    def GetHistory(self, getAll = 0):
        id = self.GetHistoryID()
        all = settings.public.generic.Get('editHistory', {})
        if getAll:
            return (id, all.get(id, []), all)
        return (id, all.get(id, []))



    def GetHistoryID(self):
        id = ''
        item = self
        while item.parent:
            id = '/' + item.name + id
            item = item.parent

        return id



    def SetReadOnly(self, state):
        self.readonly = state



    def SetMaxLength(self, maxLength):
        self.maxletters = maxLength



    def SetHistoryVisibility(self, status):
        self.displayHistory = status



    def SetPasswordChar(self, char):
        self.passwordchar = char



    def OnSetFocus(self, *args):
        if not self.readonly:
            sm.GetService('ime').SetFocus(self)
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and getattr(self.parent.parent.sr, 'node', None):
                browser = uiutil.GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_DISABLED
        if self.integermode or self.floatmode:
            self.SetText(self.text)
            self.caretIndex = self.GetCursorFromIndex(-1)
        self.ShowCaret()
        if self.autoselect:
            self.SelectAll()
        self.sr.hinttext.state = uiconst.UI_HIDDEN



    def OnKillFocus(self, *args):
        if not self.readonly:
            sm.GetService('ime').KillFocus(self)
        if self.autoselect:
            self.SelectNone()
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_HIDDEN
        if self.integermode or self.floatmode:
            ret = self.CheckBounds(self.text, 1, allowEmpty=0, returnNoneIfOK=1)
            text = [ret, self.text][(ret == None)]
            self.SetText(text, 1)
        self.HideCaret()
        self.CloseHistoryMenu()
        self.sr.hinttext.state = uiconst.UI_DISABLED
        if self.OnFocusLost:
            uthread.new(self.OnFocusLost, self)



    def SetValue(self, text, add = 0, keepSelection = 0, updateIndex = 1, docallback = 1):
        text = text or ''
        if self.integermode or self.floatmode:
            text = self.CheckBounds(text, 0, 0)
            text = self.ConvertToComma(text)
        else:
            text = text.replace('&lt;', '<').replace('&gt;', '>')
            if self.maxletters:
                text = text[:self.maxletters]
        if updateIndex:
            self.SetText(text, 0)
            self.caretIndex = self.GetCursorFromIndex(-1)
        self.SetText(text, 1)
        self.selFrom = self.selTo = None
        self.RefreshSelectionDisplay()
        self.OnTextChange(docallback)



    def GetValue(self, refreshDigits = 1, raw = 0, registerHistory = 1):
        ret = self.text
        if refreshDigits and (self.integermode or self.floatmode):
            ret = self.CheckBounds(ret, 0)
        if self.integermode:
            ret = ret or 0
            try:
                ret = int(ret)
            except:
                ret = 0
                sys.exc_clear()
        elif self.floatmode:
            ret = ret or 0
            floatdigits = self.floatmode[2]
            try:
                ret = round(float(ret), floatdigits)
            except:
                ret = 0.0
                sys.exc_clear()
        elif not raw:
            ret = ret.replace('<', '&lt;').replace('>', '&gt;')
        if registerHistory:
            self.RegisterHistory()
        return ret



    def IntMode(self, minint = None, maxint = None):
        if maxint is None:
            maxint = sys.maxint
        self.integermode = (minint, min(sys.maxint, maxint))
        self.floatmode = None
        self.OnMouseWheel = self.MouseWheel
        if minint and not self.text:
            self.SetValue(minint)



    def FloatMode(self, minfloat = None, maxfloat = None, digits = 1):
        self.floatmode = (minfloat, maxfloat, int(digits))
        self.integermode = None
        self.OnMouseWheel = self.MouseWheel
        if minfloat and not self.text:
            self.SetValue(minfloat)



    def MouseWheel(self, *args):
        if self.integermode:
            val = uicore.uilib.dz / 120
            shift = val * val * val
            if shift > 0:
                shift = max(1, long(shift))
            else:
                shift = min(-1, long(shift))
            errorValue = self.integermode[0] or 0
        elif self.floatmode:
            val = uicore.uilib.dz / 120.0
            shift = val * val * val * (1 / float(10 ** self.floatmode[2]))
            errorValue = self.floatmode[0] or 0
        else:
            return 
        try:
            current = self.GetValue(registerHistory=0)
        except ValueError:
            current = errorValue
            sys.exc_clear()
        text = self.CheckBounds(repr(current + shift), 0)
        if self.floatmode:
            floatdigits = self.floatmode[2]
            text = '%%.%df' % floatdigits % float(text)
            text = self.ConvertToComma(text)
        self.SetText(str(text))
        self.caretIndex = self.GetCursorFromIndex(self.caretIndex[0])
        self.OnTextChange()



    def OnDblClick(self, *args):
        self.caretIndex = self.GetIndexUnderCursor()
        self.selFrom = self.GetCursorFromIndex(0)
        self.selTo = self.caretIndex = self.GetCursorFromIndex(-1)
        self.RefreshCaretPosition()
        self.RefreshSelectionDisplay()



    def OnMouseDown(self, button, *etc):
        if uicore.uilib.mouseTravel > 10:
            return 
        if hasattr(self, 'RegisterFocus'):
            self.RegisterFocus(self)
        gettingFocus = uicore.registry.GetFocus() != self
        if gettingFocus:
            uicore.registry.SetFocus(self)
        leftClick = button == uiconst.MOUSELEFT
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            if self.selFrom is None:
                self.selFrom = self.caretIndex
            self.selTo = self.caretIndex = self.GetIndexUnderCursor()
            self.RefreshCaretPosition()
            self.RefreshSelectionDisplay()
        elif leftClick:
            self.caretIndex = self.mouseDownCaretIndex = self.GetIndexUnderCursor()
            self.selFrom = None
            self.selTo = None
            self.RefreshCaretPosition()
            self.RefreshSelectionDisplay()
            if self.autoselect and gettingFocus:
                self.SelectAll()
            else:
                self.sr.selectionTimer = base.AutoTimer(50, self.UpdateSelection)



    def SetSelection(self, start, end):
        if start < 0:
            start = len(self.text)
        self.selFrom = self.GetCursorFromIndex(start)
        if end < 0:
            end = -1
        self.selTo = self.caretIndex = self.GetCursorFromIndex(end)
        self.RefreshCaretPosition()
        self.RefreshSelectionDisplay()



    def UpdateSelection(self):
        oldCaretIndex = self.mouseDownCaretIndex
        newCaretIndex = self.GetIndexUnderCursor()
        self.selFrom = oldCaretIndex
        self.selTo = newCaretIndex
        self.caretIndex = newCaretIndex
        self.RefreshCaretPosition()
        self.RefreshSelectionDisplay()



    def SelectNone(self):
        self.selFrom = (None, None)
        self.selTo = (None, None)
        self.RefreshSelectionDisplay()



    def OnMouseUp(self, *args):
        self.mouseDownCaretIndex = None
        self.sr.selectionTimer = None



    def GetIndexUnderCursor(self):
        (l, t,) = self.sr.text.GetAbsolutePosition()
        cursorXpos = uicore.uilib.x - l
        return self.sr.text.GetIndexUnderPos(cursorXpos)



    def GetCursorFromIndex(self, index):
        return self.sr.text.GetWidthToIndex(index)



    def RefreshCaretPosition(self):
        self.GetCaret()
        self.sr.caret.left = self.sr.text.left + self.caretIndex[1] - 1
        if not (self.integermode or self.floatmode):
            (w, h,) = self.sr.content.GetAbsoluteSize()
            if self.sr.text.textwidth < w - self.TEXTLEFTMARGIN - self.TEXTRIGHTMARGIN:
                self.sr.text.left = self.TEXTLEFTMARGIN
            elif self.sr.text.left + self.sr.text.textwidth < w - self.TEXTLEFTMARGIN - self.TEXTRIGHTMARGIN:
                self.sr.text.left = w - self.TEXTLEFTMARGIN - self.TEXTRIGHTMARGIN - self.sr.text.textwidth
            if self.sr.caret.left > w - self.TEXTRIGHTMARGIN:
                diff = self.sr.caret.left - w + self.TEXTRIGHTMARGIN
                self.sr.text.left -= diff
            elif self.sr.caret.left < self.TEXTLEFTMARGIN:
                diff = -self.sr.caret.left + self.TEXTLEFTMARGIN
                self.sr.text.left += diff
            self.sr.caret.left = self.sr.text.left + self.caretIndex[1] - 1



    def ShowCaret(self):
        self.GetCaret()
        self.RefreshCaretPosition()
        (w, h,) = self.GetAbsoluteSize()
        self.sr.caret.height = h - 2
        self.sr.caret.state = uiconst.UI_DISABLED
        self.sr.caretTimer = base.AutoTimer(400, self.BlinkCaret)


    ShowCursor = ShowCaret

    def HideCaret(self):
        self.sr.caretTimer = None
        if self.sr.get('caret', None):
            self.sr.caret.state = uiconst.UI_HIDDEN


    HideCursor = HideCaret

    def GetCaret(self):
        if not self.sr.get('caret', None) and not self.destroyed:
            self.Prepare_Caret_()



    def BlinkCaret(self):
        if self.destroyed:
            self.sr.caretTimer = None
            return 
        if self.sr.get('caret', None):
            if not blue.rot.GetInstance('app:/App').IsActive():
                self.sr.caret.state = uiconst.UI_HIDDEN
                return 
            self.sr.caret.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][(self.sr.caret.state == uiconst.UI_HIDDEN)]



    def OnChar(self, char, flag):
        if self.OnAnyChar(char):
            if char in [127, uiconst.VK_BACK]:
                if self.GetSelectionBounds() != (None, None):
                    self.DeleteSelected()
                else:
                    self.Delete(0)
                self.CheckHistory()
                if self.OnInsert:
                    self.OnInsert(char, flag)
                return True
            if char != uiconst.VK_RETURN:
                self.Insert(char)
                self.CheckHistory()
                if self.OnInsert:
                    self.OnInsert(char, flag)
                return True
        return False



    def OnAnyChar(self, char, *args):
        return True



    def Confirm(self, *args):
        if self.OnReturn:
            self.CloseHistoryMenu()
            return uthread.new(self.OnReturn)
        searchFrom = uiutil.GetWindowAbove(self)
        if searchFrom:
            wnds = [ w for w in searchFrom.Find('trinity.Tr2Sprite2dContainer') + searchFrom.Find('trinity.Tr2Sprite2d') if getattr(w, 'btn_default', 0) == 1 ]
            if len(wnds):
                for wnd in wnds:
                    if self == wnd:
                        continue
                    if uiutil.IsVisible(wnd):
                        if hasattr(wnd, 'OnClick'):
                            uthread.new(wnd.OnClick, wnd)
                        return True

        return False



    def OnKeyDown(self, vkey, flag):
        HOME = uiconst.VK_HOME
        END = uiconst.VK_END
        CTRL = uicore.uilib.Key(uiconst.VK_CONTROL)
        SHIFT = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not self or self.destroyed:
            return 
        oldCaretIndex = self.caretIndex
        selection = self.GetSelectionBounds()
        index = self.caretIndex[0]
        if vkey == uiconst.VK_LEFT:
            if CTRL:
                index = self.text.rfind(' ', 0, max(index - 1, 0)) + 1 or 0
            else:
                index = max(index - 1, 0)
        elif vkey == uiconst.VK_RIGHT:
            if CTRL:
                index = self.text.find(' ', index) + 1 or len(self.text)
            else:
                index = index + 1
        elif vkey == HOME:
            index = 0
        elif vkey == END:
            index = len(self.text)
        elif vkey in (uiconst.VK_DELETE,):
            if self.GetSelectionBounds() != (None, None):
                self.DeleteSelected()
                return 
            self.Delete(1)
        else:
            if vkey in (uiconst.VK_UP, uiconst.VK_DOWN):
                self.BrowseHistory(vkey == uiconst.VK_DOWN)
            else:
                self.OnUnusedKeyDown(self, vkey, flag)
            return 
        self.caretIndex = self.GetCursorFromIndex(index)
        if vkey in (uiconst.VK_LEFT,
         uiconst.VK_RIGHT,
         HOME,
         END):
            if SHIFT:
                if self.selTo is not None:
                    self.selTo = self.caretIndex
                elif self.selTo is None:
                    self.selFrom = oldCaretIndex
                    self.selTo = self.caretIndex
            elif selection != (None, None):
                if vkey == uiconst.VK_LEFT:
                    index = selection[0][0]
                elif vkey == uiconst.VK_RIGHT:
                    index = selection[1][0]
                self.caretIndex = self.GetCursorFromIndex(index)
            if not SHIFT or self.selFrom == self.selTo:
                self.selFrom = self.selTo = None
            self.CloseHistoryMenu()
        self.RefreshCaretPosition()
        self.RefreshSelectionDisplay()



    def OnUnusedKeyDown(self, *args):
        pass



    def PrepareNumber(self, numberString):
        if self.integermode:
            return filter(lambda x: x in '-0123456789', numberString)
        if self.floatmode:
            return filter(lambda x: x in '%s%s' % ('-0123456789e', self.DECIMAL), numberString)
        return numberString



    def Insert(self, ins):
        if self.readonly:
            return None
        if type(ins) not in types.StringTypes:
            text = unichr(ins)
        else:
            text = ins
        text = text.replace(u'\r', u' ').replace(u'\n', u'')
        current = self.GetText()
        if self.GetSelectionBounds() != (None, None):
            self.DeleteSelected()
        if (self.integermode or self.floatmode) and text:
            if self.floatmode:
                if self.DECIMAL in text and self.DECIMAL in self.text:
                    uicore.Message('uiwarning03')
                    return None
            if text == u'-':
                newvalue = self.text[:self.caretIndex[0]] + text + self.text[self.caretIndex[0]:]
                if newvalue != u'-':
                    newvalue = self.PrepareNumber(newvalue)
                    try:
                        if self.integermode:
                            long(newvalue)
                        else:
                            float(newvalue)
                    except ValueError as e:
                        uicore.Message('uiwarning03')
                        sys.exc_clear()
                        return None
            elif text != self.DECIMAL:
                text = self.PrepareNumber(text)
                try:
                    if self.integermode:
                        long(text)
                    else:
                        float(text)
                except ValueError as e:
                    uicore.Message('uiwarning03')
                    sys.exc_clear()
                    return None
            elif text not in '0123456789' and self.integermode:
                uicore.Message('uiwarning03')
                return None
        before = self.text[:self.caretIndex[0]]
        after = self.text[self.caretIndex[0]:]
        become = before + text + after
        if self.maxletters and len(become) > self.maxletters:
            become = become[:self.maxletters]
            uicore.Message('uiwarning03')
        if (self.integermode or self.floatmode) and become and become[-1] not in (self.DECIMAL, '-'):
            become = self.PrepareNumber(become)
        self.SetText(become)
        index = self.caretIndex[0] + len(text)
        self.caretIndex = self.GetCursorFromIndex(index)
        self.OnTextChange()



    def GetMenu(self):
        m = []
        (start, end,) = self.GetSelectionBounds()
        if start is not None:
            start = start[0]
        if end is not None:
            end = end[0]
        m += [(mls.UI_CMD_COPY, self.Copy, (start, end))]
        if not self.readonly:
            sm.GetService('ime').GetMenuDelegate(self, None, m)
            paste = uiutil.GetClipboardData()
            if paste:
                m += [(mls.UI_CMD_PASTE, self.Paste, (paste,
                   start,
                   end,
                   True))]
            if self.displayHistory and self.passwordchar is None:
                m += [(mls.UI_GENERIC_CLEARHISTORY, self.ClearHistory, (None,))]
        return m



    def OnTextChange(self, docallback = 1):
        self.CheckHintText()
        self.RefreshCaretPosition()
        if docallback and self.OnChange:
            self.OnChange(self.text)



    def CheckBounds(self, qty, warnsnd = 0, allowEmpty = 1, returnNoneIfOK = 0):
        if allowEmpty and not qty:
            return ''
        if qty == '-' or qty is None:
            qty = 0
        isInt = self.integermode is not None
        isFloat = self.floatmode is not None
        if not (isInt or isFloat):
            return str(qty)
        if isFloat:
            qty = self.ConvertToComma(qty)
            pQty = self.PrepareNumber(repr(qty))
            pQty = self.ConvertToPoint(pQty)
            (minbound, maxbound,) = self.floatmode[:2]
            if pQty in (',', '.'):
                uicore.Message('uiwarning03')
                ret = minbound if minbound is not None else ''
                return ret
            if pQty.find('-') > 0:
                uicore.Message('uiwarning03')
                if minbound is not None:
                    return minbound
                return ''
            qty = float(pQty or '0')
        else:
            pQty = self.PrepareNumber(repr(qty))
            (minbound, maxbound,) = self.integermode
            if pQty.find('-') > 0:
                uicore.Message('uiwarning03')
                if minbound is not None:
                    return minbound
                return ''
            qty = long(pQty or '0')
        warn = 0
        ret = qty
        if maxbound is not None and qty > maxbound:
            warn = 1
            ret = maxbound
        elif minbound is not None and qty < minbound:
            warn = 1
            ret = minbound
        elif returnNoneIfOK:
            return 
        if warn and warnsnd:
            uicore.Message('uiwarning03')
        return ret



    def RefreshSelectionDisplay(self):
        selection = self.GetSelectionBounds()
        if selection != (None, None):
            self.GetSelectionLayer()
            (f, t,) = selection
            self.sr.selection.left = self.sr.text.left + f[1]
            self.sr.selection.width = t[1] - f[1]
            self.sr.selection.state = uiconst.UI_DISABLED
        elif self.sr.selection:
            self.sr.selection.state = uiconst.UI_HIDDEN



    def GetSelectionBounds(self):
        if self.selFrom and self.selTo and self.selFrom[0] != self.selTo[0]:
            return (min(self.selFrom, self.selTo), max(self.selFrom, self.selTo))
        return (None, None)



    def GetSelectionLayer(self):
        if not self.sr.get('selection', None):
            (l, t, w, h,) = self.GetAbsolute()
            self.sr.selection = uicls.Fill(parent=self.sr.content, name='selection', align=uiconst.TOPLEFT, pos=(0,
             1,
             0,
             h - 2), idx=1)



    def DeleteSelected(self):
        if self.readonly:
            return 
        (start, end,) = self.GetSelectionBounds()
        self.selFrom = self.selTo = None
        self.RefreshSelectionDisplay()
        text = self.GetText()
        self.SetText(text[:start[0]] + text[end[0]:])
        self.caretIndex = start
        self.OnTextChange()



    def SelectAll(self):
        self.selFrom = self.GetCursorFromIndex(0)
        self.selTo = self.GetCursorFromIndex(-1)
        self.RefreshSelectionDisplay()



    def Copy(self, selectStart = None, selectEnd = None):
        if self.passwordchar is None:
            text = self.GetText()
        else:
            text = '*' * len(self.GetText())
        if selectStart is not None and selectEnd is not None:
            blue.pyos.SetClipboardData(text[selectStart:selectEnd])
        else:
            (start, end,) = self.GetSelectionBounds()
            if not start and not end:
                blue.pyos.SetClipboardData(text)
            else:
                blue.pyos.SetClipboardData(text[start[0]:end[0]])



    def Paste(self, paste, deleteStart = None, deleteEnd = None, forceFocus = False):
        hadFocus = uicore.registry.GetFocus() == self
        if deleteStart is None or deleteEnd is None:
            (start, end,) = self.GetSelectionBounds()
            if start is not None and end is not None:
                self.DeleteSelected()
        else:
            text = self.GetText()
            self.SetText(text[:deleteStart] + text[deleteEnd:])
            self.caretIndex = self.GetCursorFromIndex(deleteStart)
            self.OnTextChange()
        self.Insert(paste)
        if hadFocus or forceFocus:
            uicore.registry.SetFocus(self)



    def EncodeOutput(self, otext):
        if not otext:
            return ''
        if self.integermode or self.floatmode:
            elem = [ each for each in otext if each not in ('-', '.') ]
            if not len(elem):
                return ''
        if self.integermode:
            return util.FmtAmt(long(float(otext)))
        if self.floatmode:
            otext = self.ConvertToPoint(otext)
            return util.FmtAmt(float(otext), showFraction=self.floatmode[2], fillWithZero=True)
        if not isinstance(otext, basestring):
            otext = str(otext)
        return otext



    def GetText(self):
        return self.text



    def SetText(self, text, format = 0):
        if not isinstance(text, basestring):
            if self.integermode:
                text = repr(int(text))
            elif self.floatmode:
                text = '%.*f' % (self.floatmode[2], float(text))
                text = self.ConvertToComma(text)
            else:
                text = str(text)
        if self.passwordchar is not None:
            displayText = self.passwordchar * len(text.replace('<br>', ''))
        elif format:
            displayText = self.EncodeOutput(text) + self.suffix
        else:
            displayText = text
        self.sr.text.text = displayText.replace('<', '&lt;').replace('>', '&gt;')
        self.text = text



    def Delete(self, direction = 1):
        if self.readonly:
            return 
        if direction:
            begin = self.caretIndex[0]
            newCaretIndex = self.caretIndex[0]
            end = min(self.caretIndex[0] + 1, len(self.text))
        else:
            end = self.caretIndex[0]
            begin = max(self.caretIndex[0] - 1, 0)
            newCaretIndex = begin
        become = self.text[:begin] + self.text[end:]
        if not become and (self.floatmode or self.integermode):
            if self.floatmode:
                (minbound, maxbound,) = self.floatmode[:2]
            if self.integermode:
                (minbound, maxbound,) = self.integermode
            if minbound <= 0 <= maxbound:
                become = ''
        self.SetText(become)
        newCaretIndex = min(newCaretIndex, len(self.text))
        self.caretIndex = self.GetCursorFromIndex(newCaretIndex)
        self.OnTextChange()



    def ConvertToPoint(self, qty):
        ret = qty
        if self.floatmode and self.DECIMAL == ',':
            ret = uiutil.ConvertDecimal(qty, ',', '.')
        return ret



    def ConvertToComma(self, qty, numDecimals = 0):
        ret = qty
        if self.floatmode and self.DECIMAL == ',':
            ret = uiutil.ConvertDecimal(qty, '.', ',', numDecimals=self.floatmode[2])
        return ret




