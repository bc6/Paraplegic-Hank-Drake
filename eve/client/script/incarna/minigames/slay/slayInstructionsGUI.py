import util
import uicls
import uiutil
import uiconst

class SlayInstructionsGUI(uicls.Window):
    __guid__ = 'minigames.SlayInstructionsGUI'
    default_width = 300
    default_height = 450
    default_minSize = (300, 450)
    currPage = 1
    maxPages = 7
    instructions = {}
    pictureInstructions = {}

    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush



    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.sr.main = uiutil.GetChild(self, 'main')
        uicls.Line(align=uiconst.TOTOP, parent=self.sr.main)
        self.infoContainer = uicls.Container(name='infoContainer', align=uiconst.TOALL, left=5, top=0, state=uiconst.UI_NORMAL, parent=self.sr.main, autoHeight=False, autoWidth=False)
        self.prevBtn = uicls.Button(parent=self.infoContainer, label='Previous', func=self.Previous, align=uiconst.BOTTOMLEFT)
        self.prevBtn.width = 80
        self.nextBtn = uicls.Button(parent=self.infoContainer, label='Next', func=self.Next, align=uiconst.BOTTOMRIGHT)
        self.nextBtn.width = 80
        self.LoadCurrPage()



    def Previous(self, *args):
        if self.currPage > 1:
            self.currPage -= 1
            self.LoadCurrPage()



    def Next(self, *args):
        if self.currPage < self.maxPages:
            self.currPage += 1
            self.LoadCurrPage()



    def LoadCurrPage(self):
        self.SetWndIcon('40_1%d' % (self.currPage - 1))
        self.SetCaption(self.instructions[self.currPage].title)
        if hasattr(self, 'infoPic'):
            self.infoPic.Close()
        self.infoPic = uicls.Container(name='infoPic', width=200, height=193, left=0, top=30, align=uiconst.CENTERBOTTOM, state=uiconst.UI_NORMAL, parent=self.sr.main)
        infoSprite = uicls.Sprite(name='infoSprite', parent=self.infoPic, texturePath=self.pictureInstructions[self.currPage], align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 1.0))
        if hasattr(self, 'heading'):
            self.heading.Close()
        self.heading = uicls.Label(text=self.instructions[self.currPage].title, parent=self.sr.main, align=uiconst.TOPLEFT, left=65, top=-40, width=self.width - 10, height=self.height - 10, autoWidth=False, autoHeight=False, fontsize=25, singleline=True, uppercase=1)
        if hasattr(self, 'helpText'):
            self.helpText.Close()
        text = self.instructions[self.currPage].content
        self.helpText = uicls.Label(text=text, parent=self.infoContainer, align=uiconst.TOALL, left=5, top=5, autowidth=False, autoheight=False, fontsize=11, uppercase=0)




