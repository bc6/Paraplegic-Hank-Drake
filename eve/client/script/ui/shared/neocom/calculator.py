import sys
import uix
import uiutil
import xtriui
import uicls
import uiconst
import localization
import localizationUtil

class Calculator(uicls.Window):
    __guid__ = 'form.Calculator'
    default_windowID = 'calculator'
    default_width = 167
    default_height = 160
    default_left = 0
    default_top = 0

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'all'
        self.SetCaption(localization.GetByLabel('UI/Accessories/Calculator/Calculator'))
        self.MakeUnResizeable()
        self.SetWndIcon('ui_49_64_1')
        self.HideMainIcon()
        self.SetTopparentHeight(21)
        uicls.Container(name='psuh', parent=self.sr.topParent, align=uiconst.TOLEFT, width=const.defaultPadding, idx=0)
        iconPar = uicls.Container(name='iconPar', parent=self.sr.topParent, align=uiconst.TORIGHT, width=18, idx=0)
        icon = xtriui.MiniButton(icon='ui_38_16_156', parent=iconPar, top=2, size=16, align=uiconst.RELATIVE)
        icon.groupID = 'viewMode'
        self.sr.viewModeBtn = icon
        icon.Click = self.ViewModeBtnClick
        inpt = uicls.SinglelineEdit(name='inpt', parent=self.sr.topParent, align=uiconst.TOTOP)
        inpt.OnChar = self.OnCharInput
        inpt.Paste = self.OnInputPasted
        self.sr.inpt = inpt
        self.SetInpt('0')
        hist = settings.public.ui.Get('CalculatorHistory', [])
        if hist:
            ops = [ (v, v) for v in hist ]
        else:
            ops = [('0', '0')]
        inpt.LoadCombo('urlcombo', ops, self.OnComboChange)
        self.sr.mem = uicls.Container(name='mem', parent=self.sr.main, left=const.defaultPadding, top=3, height=16, align=uiconst.TOTOP)
        self.sr.work = uicls.Container(name='work', parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        size = 24
        self.buttons = [(0,
          0,
          '7',
          localizationUtil.FormatNumeric(7)),
         (1,
          0,
          '8',
          localizationUtil.FormatNumeric(8)),
         (2,
          0,
          '9',
          localizationUtil.FormatNumeric(9)),
         (3,
          0,
          'divide',
          localization.GetByLabel('UI/Accessories/Calculator/DivideSymbol')),
         (0,
          1,
          '4',
          localizationUtil.FormatNumeric(4)),
         (1,
          1,
          '5',
          localizationUtil.FormatNumeric(5)),
         (2,
          1,
          '6',
          localizationUtil.FormatNumeric(6)),
         (3,
          1,
          'times',
          localization.GetByLabel('UI/Accessories/Calculator/MultiplySymbol')),
         (0,
          2,
          '1',
          localizationUtil.FormatNumeric(1)),
         (1,
          2,
          '2',
          localizationUtil.FormatNumeric(2)),
         (2,
          2,
          '3',
          localizationUtil.FormatNumeric(3)),
         (3,
          2,
          'minus',
          localization.GetByLabel('UI/Accessories/Calculator/SubtractSymbol')),
         (0,
          3,
          '0',
          localizationUtil.FormatNumeric(0)),
         (1,
          3,
          'dot',
          localization.GetByLabel('UI/Accessories/Calculator/DotSymbol')),
         (2,
          3,
          'equal',
          localization.GetByLabel('UI/Accessories/Calculator/EqualsSymbol')),
         (3,
          3,
          'plus',
          localization.GetByLabel('UI/Accessories/Calculator/AddSymbol')),
         (4.5,
          0,
          'clear',
          localization.GetByLabel('UI/Accessories/Calculator/ClearSymbol')),
         (5.5,
          0,
          'clearall',
          localization.GetByLabel('UI/Accessories/Calculator/ClearAllSymbol')),
         (4.5,
          1,
          'bo',
          localization.GetByLabel('UI/Accessories/Calculator/BracketOpenSymbol')),
         (5.5,
          1,
          'bc',
          localization.GetByLabel('UI/Accessories/Calculator/BracketCloseSymbol')),
         (4.5,
          2,
          'percent',
          localization.GetByLabel('UI/Accessories/Calculator/PercentSymbol')),
         (5.5,
          2,
          'square',
          localization.GetByLabel('UI/Accessories/Calculator/SquareSymbol')),
         (4.5,
          3,
          'plusminus',
          localization.GetByLabel('UI/Accessories/Calculator/PlusMinusSymbol')),
         (5.5, 3, 'root', u'\u221a&macr;')]
        for (x, y, label, cap,) in self.buttons:
            btn = uix.GetBigButton(size=size, where=self.sr.work, left=int(x * size), top=int(y * size), iconMargin=10, align=uiconst.RELATIVE)
            btn.SetInCaption(cap)
            btn.Click = self.OnBtnClick
            btn.OnDblClick = None
            btn.name = label
            setattr(self.sr, 'btn%s' % label, btn)

        uicls.Line(parent=self.sr.mem, align=uiconst.TOTOP)
        uicls.Line(parent=self.sr.mem, align=uiconst.TOBOTTOM)
        for i in xrange(1, 7):
            opt = uicls.WindowDropDownMenu(name='memoption', parent=self.sr.mem, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
            opt.Setup(localization.GetByLabel('UI/Accessories/Calculator/AbbreviatedMemory', index=i), getattr(self, 'GetMem%sMenu' % i, None))
            opt.OnClick = (self.OnClickMemory, opt)
            opt.sr.memHilite = uicls.Fill(parent=opt, color=(0.0, 0.0, 1.0, 0.2), state=uiconst.UI_HIDDEN)
            opt.name = 'mem%s' % i
            opt.label = settings.public.ui.Get('CalculatorMem%sName' % i, localization.GetByLabel('UI/Accessories/Calculator/Memory', index=i))
            if i == 1:
                opt.left = const.defaultPadding
            setattr(self.sr, 'memBtn%s' % i, opt)
            opt.mem = settings.public.ui.Get('CalculatorMem%s' % i, None)
            opt.nr = i
            if opt.mem:
                opt.hint = '%s:<br>%s' % (opt.label, opt.mem)
                opt.sr.memHilite.state = uiconst.UI_DISABLED
            else:
                opt.hint = localization.GetByLabel('UI/Accessories/Calculator/EmptyBank', label=opt.label, empty=localization.GetByLabel('UI/Accessories/Calculator/Empty'))
                opt.sr.memHilite.state = uiconst.UI_HIDDEN

        self.SetLayout()
        self.digitSign = prefs.GetValue('digit', '.')
        self.decimalSign = prefs.GetValue('decimal', '.')
        self.newNumber = True
        self.stack = []
        self.opStack = []
        self.lastOp = 0
        uicore.registry.SetFocus(self.sr.inpt)



    def SetLayout(self):
        expanded = settings.public.ui.Get('CalculatorExpanded', 1)
        if expanded:
            self.SetMinSize([167, 160], 1)
            h = uiconst.UI_NORMAL
            self.sr.viewModeBtn.hint = localization.GetByLabel('UI/Accessories/Calculator/HideButtons')
        else:
            self.SetMinSize([167, 60], 1)
            h = uiconst.UI_HIDDEN
            self.sr.viewModeBtn.hint = localization.GetByLabel('UI/Accessories/Calculator/ShowButtons')
        for (x, y, label, cap,) in self.buttons:
            btn = self.sr.Get('btn%s' % label, None)
            btn.state = h




    def MouseDown(self, *args):
        uicore.registry.SetFocus(self.sr.inpt)



    def SetInpt(self, value, new = True):
        self.sr.inpt.SetValue(value)
        self.newNumber = new



    def OnComboChange(self, combo, header, value, *args):
        self.SetInpt(value, False)



    def OnInputPasted(self, paste, deleteStart = None, deleteEnd = None):
        self.SetInpt('0')
        for char in paste:
            self.OnCharInput(ord(char))




    def OnCharInput(self, char, flag = None):
        _char = char
        text = self.sr.inpt.GetText()
        try:
            _char = unichr(char)
            if len(_char) == 1 and _char in '0123456789':
                if text == '0' or self.newNumber:
                    self.sr.inpt.text = ''
                self.sr.inpt.Insert(char)
                self.newNumber = False
                return True
        except:
            sys.exc_clear()
        if _char in self.knownkeys.keys():
            _char = self.knownkeys[_char]
        if _char == 'dot' or type(char) == int and unichr(char) == u'.':
            if self.decimalSign not in text or self.newNumber:
                if text == '' or self.newNumber:
                    self.sr.inpt.text = '0'
                    self.sr.inpt.Insert(ord(self.decimalSign))
                    self.newNumber = False
                    return True
                self.sr.inpt.Insert(ord(self.decimalSign))
                self.newNumber = False
            else:
                return True
        if _char == 'plusminus':
            if text.startswith('-'):
                text = text[1:]
            else:
                text = '-' + text
            self.SetInpt(text, False)
            return True
        if _char == 'clearall':
            self.stack = []
            self.opStack = []
        if _char in ('\x08', 'clear', 'clearall'):
            self.SetInpt('0')
            return True
        if _char in self.prio.keys():
            self.Operator(_char, text)
            if _char == 'equal':
                hist = settings.public.ui.Get('CalculatorHistory', [])
                hist.insert(0, text)
                if len(hist) > 20:
                    hist.pop()
                settings.public.ui.Set('CalculatorHistory', hist)
                ops = [ (v, v) for v in hist ]
                self.sr.inpt.LoadCombo('urlcombo', ops, self.OnComboChange, setvalue=text)
        return True



    def OnBtnClick(self, btn, *args):
        try:
            char = ord(btn.name)
        except:
            char = btn.name
            sys.exc_clear()
        self.OnCharInput(char)



    def ViewModeBtnClick(self):
        expanded = settings.public.ui.Get('CalculatorExpanded', 1)
        expanded ^= 1
        settings.public.ui.Set('CalculatorExpanded', expanded)
        self.SetLayout()



    def OnClickMemory(self, btn, *args):
        if getattr(btn, 'mem', None) is not None:
            self.SetInpt(str(btn.mem), False)



    def GetMem1Menu(self):
        return self.GetMemMenu(self.sr.memBtn1)



    def GetMem2Menu(self):
        return self.GetMemMenu(self.sr.memBtn2)



    def GetMem3Menu(self):
        return self.GetMemMenu(self.sr.memBtn3)



    def GetMem4Menu(self):
        return self.GetMemMenu(self.sr.memBtn4)



    def GetMem5Menu(self):
        return self.GetMemMenu(self.sr.memBtn5)



    def GetMem6Menu(self):
        return self.GetMemMenu(self.sr.memBtn6)



    def GetMem7Menu(self):
        return self.GetMemMenu(self.sr.memBtn7)



    def GetMem8Menu(self):
        return self.GetMemMenu(self.sr.memBtn8)



    def GetMemMenu(self, btn):
        m = []
        m.append((localization.GetByLabel('UI/Accessories/Calculator/Set'), self.MemDo, (btn, 'Set')))
        if getattr(btn, 'mem', None) is not None:
            m.append((localization.GetByLabel('UI/Accessories/Calculator/Add'), self.MemDo, (btn, 'Add')))
            m.append((localization.GetByLabel('UI/Accessories/Calculator/Subtract'), self.MemDo, (btn, 'Sub')))
            m.append((localization.GetByLabel('UI/Accessories/Calculator/Clear'), self.MemDo, (btn, 'Clear')))
        m.append((localization.GetByLabel('UI/Accessories/Calculator/Annotate'), self.MemDo, (btn, 'Name')))
        return m



    def MemDo(self, mem, command):
        if self.sr.inpt.GetValue() == '':
            self.SetInpt('0')
        if command == 'Set':
            setattr(mem, 'mem', float(self.sr.inpt.GetValue()))
            mem.sr.memHilite.state = uiconst.UI_DISABLED
        elif command == 'Add':
            setattr(mem, 'mem', getattr(mem, 'mem', 0.0) + float(self.sr.inpt.GetValue()))
        elif command == 'Sub':
            setattr(mem, 'mem', getattr(mem, 'mem', 0.0) - float(self.sr.inpt.GetValue()))
        elif command == 'Clear':
            setattr(mem, 'mem', None)
            mem.sr.memHilite.state = uiconst.UI_HIDDEN
        elif command == 'Name':
            format = [{'type': 'edit',
              'setvalue': getattr(mem, 'label', '') or '',
              'labelwidth': 48,
              'label': localization.GetByLabel('UI/Accessories/Calculator/Name'),
              'key': 'name',
              'maxlength': 16,
              'setfocus': 1}]
            retval = uix.HybridWnd(format, localization.GetByLabel('UI/Accessories/Calculator/Annotate'), icon=uiconst.QUESTION, minW=300, minH=100)
            if retval:
                mem.label = retval['name']
                settings.public.ui.Set('CalculatorMem%sName' % mem.nr, mem.label)
        if getattr(mem, 'mem', None) is not None:
            mem.hint = '%s<br>%.14G' % (mem.label, getattr(mem, 'mem', 0.0))
        else:
            mem.hint = localization.GetByLabel('UI/Accessories/Calculator/EmptyBank', label=mem.label, empty=localization.GetByLabel('UI/Accessories/Calculator/Empty'))
        settings.public.ui.Set('CalculatorMem%s' % mem.nr, getattr(mem, 'mem', None))



    def CheckOperator(self):
        if str(self.stack[-1]) in self.prio.keys():
            return True
        return False



    def Calc(self):
        if len(self.stack) > 0 and self.CheckOperator():
            op = self.stack.pop()
            if op in ('equal', 'bo', 'bc'):
                self.Calc()
            if op == 'plus':
                self.Calc()
                op1 = self.stack.pop()
                self.Calc()
                op2 = self.stack.pop()
                self.stack.append(op2 + op1)
            if op == 'minus':
                self.Calc()
                op1 = self.stack.pop()
                self.Calc()
                op2 = self.stack.pop()
                self.stack.append(op2 - op1)
            if op == 'times':
                self.Calc()
                op1 = self.stack.pop()
                self.Calc()
                op2 = self.stack.pop()
                self.stack.append(op2 * op1)
            if op == 'divide':
                self.Calc()
                op1 = self.stack.pop()
                self.Calc()
                op2 = self.stack.pop()
                try:
                    self.stack.append(op2 / op1)
                except ZeroDivisionError as e:
                    sys.exc_clear()
                    eve.Message('uiwarning03')
                    self.stack.append(0.0)
            if op == 'square':
                self.Calc()
                op1 = self.stack.pop()
                try:
                    self.stack.append(op1 ** 2.0)
                except OverflowError as e:
                    sys.exc_clear()
                    eve.Message('uiwarning03')
                    self.stack.append(0.0)
            if op == 'root':
                self.Calc()
                op1 = self.stack.pop()
                try:
                    self.stack.append(op1 ** 0.5)
                except ValueError as e:
                    sys.exc_clear()
                    eve.Message('uiwarning03')
                    self.stack.append(0.0)
            if op == 'percent':
                self.Calc()
                op1 = self.stack.pop()
                if len(self.stack):
                    op2 = self.stack[-1]
                else:
                    eve.Message('uiwarning03')
                    op2 = 0.0
                self.stack.append(op2 * op1 / 100.0)



    def Operator(self, op, number):
        if not self.newNumber or len(self.stack) == 0:
            self.stack.append(float(number.replace(self.decimalSign, '.')))
        elif self.lastOp in ('plus', 'minus', 'times', 'divide') and op != 'bo':
            self.opStack[-1] = op
            return 
        if op != 'bo' and (len(self.opStack) == 0 or self.prio[op] <= self.prio[self.opStack[-1]]):
            while len(self.opStack) > 0 and self.prio[op] <= self.prio[self.opStack[-1]]:
                self.stack.append(self.opStack.pop())

        if op == 'bc':
            while len(self.opStack) > 0 and self.opStack[-1] != 'bo':
                self.stack.append(self.opStack.pop())

            if len(self.opStack):
                self.opStack.pop()
        if op in ('percent', 'root', 'square', 'equal', 'bc'):
            self.stack.append(op)
        else:
            self.opStack.append(op)
        self.Calc()
        number = '%.14G' % self.stack[-1]
        self.SetInpt(number.replace('.', self.decimalSign))
        self.lastOp = op


    knownkeys = {'+': 'plus',
     '-': 'minus',
     '*': 'times',
     '/': 'divide',
     prefs.GetValue('decimal', '.'): 'dot',
     '=': 'equal',
     'r': 'root',
     's': 'square',
     'p': 'percent',
     'm': 'plusminus',
     '(': 'bo',
     ')': 'bc',
     'C': 'clearall',
     '\r': 'equal'}
    prio = {'plus': 3,
     'minus': 3,
     'times': 4,
     'divide': 4,
     'square': 5,
     'root': 5,
     'bo': 1,
     'bc': 6,
     'percent': 4,
     'equal': 0}


