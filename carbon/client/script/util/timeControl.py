import uicls
import uiconst
import uiconst
import util
import blue

class TimeControlWindow(uicls.Window):
    __guid__ = 'uicls.TimeControlWindow'
    default_width = 250
    default_height = 150
    ENTRY_FONTSIZE = 11
    HEADER_FONTSIZE = 12
    ENTRY_FONT = 'res:/UI/Fonts/arial.ttf'
    HEADER_FONT = 'res:/UI/Fonts/arialbd.ttf'
    ENTRY_LETTERSPACE = 1
    default_caption = 'Time Control Window'
    default_minSize = (250, 150)

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        if hasattr(self, 'SetTopparentHeight'):
            self.SetTopparentHeight(0)
        self.topCont = uicls.Container(parent=self.sr.content, name='topCont', align=uiconst.TOTOP, height=120)
        self.topLeftCont = uicls.Container(parent=self.topCont, name='topLeftCont', align=uiconst.TOLEFT, width=120, padding=(3, 20, 3, 3))
        self.topRightCont = uicls.Container(parent=self.topCont, name='topRightCont', align=uiconst.TOALL, padding=(3, 10, 3, 3))
        self.mainCont = uicls.Container(parent=self.sr.main, name='mainCont')
        self.ConstructTopLeftCont()
        self.ConstructTopRightCont()



    def ConstructTopLeftCont(self):
        uicls.Line(parent=self.topLeftCont, align=uiconst.TORIGHT)
        uicls.Label(parent=self.topLeftCont, text='Select clock:', align=uiconst.TOTOP)
        uicls.Checkbox(parent=self.topLeftCont, text='Actual', groupname='clockGroup', align=uiconst.TOTOP, checked=not blue.os.useSmoothedDeltaT, callback=self.OnClockRadioButtonsChanged, retval=False)
        uicls.Checkbox(parent=self.topLeftCont, text='Smoothed', groupname='clockGroup', align=uiconst.TOTOP, checked=blue.os.useSmoothedDeltaT, callback=self.OnClockRadioButtonsChanged, retval=True)
        uicls.LabelCore(parent=self.topLeftCont, align=uiconst.TOTOP, text='Time Scaler:', pos=(0, 0, 0, 0))
        uicls.SinglelineEdit(parent=self.topLeftCont, name='timeScaler', align=uiconst.TOTOP, floats=(0.0, 100.0), setvalue=blue.os.timeScaler, OnChange=self.OnTimeScalerChanged, pos=(0, 0, 20, 12))



    def OnTimeScalerChanged(self, value):
        if value:
            blue.os.timeScaler = float(value)



    def OnClockRadioButtonsChanged(self, button):
        blue.os.useSmoothedDeltaT = button.data['value']



    def ConstructTopRightCont(self):
        cont = uicls.Container(parent=self.topRightCont, align=uiconst.TOTOP, height=75, padTop=12, padBottom=10)
        uicls.LabelCore(parent=cont, align=uiconst.TOTOP, text='Slug Min Time:', pos=(0, 0, 0, 0))
        uicls.SinglelineEdit(parent=cont, name='slugMinEdit', align=uiconst.TOTOP, ints=(0, 1000), setvalue=int(blue.os.slugTimeMinMs), OnChange=self.OnSlugMinChanged, pos=(0, 0, 100, 12))
        uicls.LabelCore(parent=cont, align=uiconst.TOTOP, text='Slug Max Time:', pos=(0, 0, 0, 0))
        uicls.SinglelineEdit(parent=cont, name='slugMaxEdit', align=uiconst.TOTOP, ints=(0, 1000), setvalue=int(blue.os.slugTimeMaxMs), OnChange=self.OnSlugMaxChanged, pos=(0, 0, 100, 12))
        uicls.Checkbox(parent=self.topRightCont, text='Use Simple Loop', align=uiconst.TOTOP, checked=blue.os.useSimpleCatchupLoop, callback=self.OnSimpleLoopChanged, padBottom=10)



    def OnSlugMinChanged(self, value):
        if value:
            blue.os.slugTimeMinMs = float(value)



    def OnSlugMaxChanged(self, value):
        if value:
            blue.os.slugTimeMaxMs = float(value)



    def OnSimpleLoopChanged(self, checkBox):
        blue.os.useSimpleCatchupLoop = checkBox.GetValue()
        blue.os.useNominalDeltaT = not blue.os.useSimpleCatchupLoop



    def ConstructMainCont(self):
        uicls.Line(parent=self.mainCont, align=uiconst.TOTOP)
        self.mainSprite = uicls.Sprite(parent=self.mainCont, name='mainSprite', pos=(0, 0, 128, 128), align=uiconst.CENTER, texturePath='res:/UI/Texture/corpLogoLibs/logolib0101.dds')




