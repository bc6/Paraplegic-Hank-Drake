#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/eveScrollArea.py
import uiconst
import uicls
import trinity
SCROLLDIRECTION_V = 1
SCROLLDIRECTION_H = 2
SCROLLBARSIZE = 10

class ScrollArea(uicls.ScrollAreaCore):
    __guid__ = 'uicls.ScrollArea'

    def Prepare_Underlay_(self):
        self.underlay = uicls.BumpedUnderlay(parent=self, name='background')

    def Prepare_ScrollControls_(self):
        self.verticalScrollControl = uicls.ScrollAreaControls(name='__verticalScrollControl', parent=self, align=uiconst.TORIGHT, width=SCROLLBARSIZE, state=uiconst.UI_HIDDEN, scroll=self, scrollDirection=SCROLLDIRECTION_V, idx=0)
        self.horizontalScrollControl = None


class ScrollAreaHandle(uicls.ScrollAreaHandleCore):
    __guid__ = 'uicls.ScrollAreaHandle'

    def Prepare_(self):
        dotFrame = uicls.Frame(name='dotFrame', parent=self, texturePath='res:/UI/Texture/Shared/windowButtonDOT.png', cornerSize=2, color=(1.0, 1.0, 1.0, 1.0), padding=(2, 1, 1, 1), spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        uicls.Sprite(parent=self, name='fill', texturePath='res:/UI/Texture/Shared/windowButtonGradient.png', state=uiconst.UI_DISABLED, padding=(2, 1, 1, 1), align=uiconst.TOALL, filter=False)
        self.Prepare_Hilite_()

    def Prepare_Hilite_(self):
        self.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.3), padding=(2, 1, 1, 1), state=uiconst.UI_HIDDEN, idx=0)


class ScrollAreaControls(uicls.ScrollAreaControlsCore):
    __guid__ = 'uicls.ScrollAreaControls'

    def Prepare_(self):
        self.Prepare_ScrollHandle_()
        self.Prepare_ScrollButtons_()
        self.underlay = uicls.Fill(name='__underlay', color=(0.0, 0.0, 0.0, 0.5), parent=self, padLeft=1)

    def Prepare_ScrollButtons_(self):
        self.scrollUpBtn = uicls.ScrollBtn(name='scrollBtnTop', parent=self, width=10, height=12, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL)
        icon = uicls.Icon(icon='ui_38_16_105', align=uiconst.CENTER, parent=self.scrollUpBtn, state=uiconst.UI_DISABLED, pos=(1, 0, 0, 0))
        self.scrollDownBtn = uicls.ScrollBtn(name='scrollBtnBottom', parent=self, width=10, height=12, align=uiconst.CENTERBOTTOM, state=uiconst.UI_NORMAL)
        icon = uicls.Icon(icon='ui_38_16_104', align=uiconst.CENTER, parent=self.scrollDownBtn, state=uiconst.UI_DISABLED, pos=(1, 0, 0, 0))
        self.scrollUpBtn.Startup(self.parent, 1)
        self.scrollDownBtn.Startup(self.parent, -1)

    def Prepare_ScrollHandle_(self):
        self.scrollhandle = uicls.ScrollAreaHandle(name='__scrollhandle', parent=self, align=uiconst.TOPLEFT, width=self.width, padding=(0, 9, 0, 9), state=uiconst.UI_NORMAL, scrollDirection=self.scrollDirection)