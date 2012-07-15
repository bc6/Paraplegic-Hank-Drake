#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/ui/control/buttongroup.py
import uicls
import uiconst
import fontConst

class ButtonGroupCore(uicls.Container):
    __guid__ = 'uicls.ButtonGroupCore'
    default_align = uiconst.TOBOTTOM
    default_state = uiconst.UI_PICKCHILDREN
    default_name = 'btnsmainparent'
    default_subalign = uiconst.CENTER
    default_valign = False
    default_line = True
    default_idx = None
    default_unisize = True
    default_forcedButtonNames = False
    default_fixedWidth = False
    default_alwaysLite = False
    default_btns = None
    default_fontsize = fontConst.DEFAULT_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.btns = attributes.get('btns', self.default_btns)
        self.subalign = attributes.get('subalign', self.default_subalign)
        self.valign = attributes.get('valign', self.default_valign)
        self.line = attributes.get('line', self.default_line)
        self.idx = attributes.get('idx', self.default_idx)
        self.unisize = attributes.get('unisize', self.default_unisize)
        self.forcedButtonNames = attributes.get('forcedButtonNames', self.default_forcedButtonNames)
        self.fixedWidth = attributes.get('fixedWidth', self.default_fixedWidth)
        self.alwaysLite = attributes.get('alwaysLite', self.default_alwaysLite)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.Prepare_Appearance_()
        if self.btns:
            for button in self.btns:
                self.AddButton(button)

    def Prepare_Appearance_(self):
        self.subpar = uicls.Container(parent=self, name='btns', state=uiconst.UI_PICKCHILDREN, align=self.subalign)
        if self.line:
            line2 = uicls.Line(parent=self, name='black', state=uiconst.UI_DISABLED, color=(0.0, 0.0, 0.0, 0.15), align=uiconst.TOTOP, padTop=-1)
            line1 = uicls.Line(parent=self, name='white', color=(1.0, 1.0, 1.0, 0.25), align=uiconst.TOTOP)

    def AddButton(self, btn):
        btnID = btn[0]
        buttonName = None
        if self.forcedButtonNames and len(btn) == 5:
            buttonName, caption, function, args, size = btn
            btnID = caption
            btn_modalresult, btn_default, btn_cancel = (0, 0, 0)
        elif len(btn) == 3:
            caption, function, args = btn
            btn_modalresult, btn_default, btn_cancel = (0, 0, 0)
        elif len(btn) == 4:
            caption, function, args, size = btn
            btn_modalresult, btn_default, btn_cancel = (0, 0, 0)
        elif len(btn) == 5:
            caption, function, args, size, btnID = btn
            btn_modalresult, btn_default, btn_cancel = (0, 0, 0)
        else:
            caption, function, args, size, btn_modalresult, btn_default, btn_cancel = btn
        if self.fixedWidth:
            fixed = size
        else:
            fixed = None
        newbtn = uicls.Button(parent=self.subpar, label=caption, func=function, args=args, btn_modalresult=btn_modalresult, btn_default=btn_default, btn_cancel=btn_cancel, alwaysLite=self.alwaysLite, fixedwidth=fixed, name=buttonName or '%s_Btn' % caption, fontStyle=self.fontStyle, fontFamily=self.fontFamily, fontPath=self.fontPath, fontsize=self.fontsize)
        self.sr.Set('%s_Btn' % caption, newbtn)
        self.ResetLayout()

    def ResetLayout(self):
        maxWidth = 0
        for btn in self.subpar.children:
            maxWidth = max(btn.width, maxWidth)

        leftCount = 0
        topCount = 0
        for btn in self.subpar.children:
            if self.unisize:
                btn.width = maxWidth
            if self.valign:
                btn.align = uiconst.CENTERTOP
                btn.left = 0
                btn.top = topCount
                topCount += btn.height + 4
            else:
                btn.align = uiconst.TOPLEFT
                btn.left = leftCount
                btn.top = 0
                leftCount += btn.width + 4

        if self.valign:
            self.subpar.width = maxWidth
            self.subpar.height = topCount - 4
        else:
            self.subpar.width = leftCount - 4
            self.subpar.height = self.subpar.children[0].height
        if self.align not in uiconst.AFFECTEDBYPUSHALIGNMENTS:
            self.width = self.subpar.width
            self.height = self.subpar.height + 8
        elif self.align in (uiconst.TOTOP, uiconst.TOBOTTOM):
            self.height = self.subpar.height + 8
        elif self.align in (uiconst.TOLEFT, uiconst.TORIGHT):
            self.width = self.subpar.width

    def GetMinimumSize(self):
        return (self.subpar.width, self.subpar.height)

    def GetBtnByLabel(self, btnLabel):
        return self.sr.Get('%s_Btn' % btnLabel)

    def GetBtnByIdx(self, idx):
        return self.subpar.children[idx]