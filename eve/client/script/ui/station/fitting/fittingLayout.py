import uicls
import uiconst
import trinity

class FittingLayout(uicls.Container):
    __guid__ = 'uicls.FittingLayout'
    default_name = 'fittingbase'
    default_width = 640
    default_height = 640
    default_align = uiconst.CENTERLEFT
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        overlay = uicls.Sprite(parent=self, name='overlay', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_overlay.png', color=(1.0, 1.0, 1.0, 0.39))
        self.sr.calibrationStatusPoly = uicls.Polygon(parent=self, name='calibrationStatusPoly', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_FILL)
        self.sr.powergridStatusPoly = uicls.Polygon(parent=self, name='powergridStatusPoly', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_FILL)
        self.sr.cpuStatusPoly = uicls.Polygon(parent=self, name='cpuStatusPoly', align=uiconst.CENTER, spriteEffect=trinity.TR2_SFX_FILL)
        baseDOT = uicls.Sprite(parent=self, name='baseDOT', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_dotproduct.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        self.sr.baseColor = uicls.Sprite(parent=self, name='baseColor', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_basecircle.png')
        self.sr.baseShape = uicls.Sprite(parent=self, name='baseShape', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase.png', color=(0.0, 0.0, 0.0, 0.86))




class FittingSlotLayout(uicls.Transform):
    __guid__ = 'uicls.FittingSlotLayout'
    default_name = 'fittingSlot'
    default_left = (256,)
    default_width = 44
    default_height = 54
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Transform.ApplyAttributes(self, attributes)
        groupParent = uicls.Transform(parent=self, name='groupParent', pos=(-10, 14, 16, 16), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        groupMark = uicls.Icon(parent=groupParent, name='groupMark', pos=(0, 0, 20, 20), align=uiconst.TOPLEFT, texturePath='ui_73_16_177')
        iconParent = uicls.Transform(parent=self, name='iconParent', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0,
         0,
         self.width,
         self.height))
        icon = uicls.Icon(parent=iconParent, name='icon', pos=(8, 8, 8, 8), align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        underlay = uicls.Icon(parent=self, name='underlay', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-10, -5, -10, -5), icon='ui_81_64_1', filter=True)
        chargeIndicator = uicls.Icon(parent=self, name='chargeIndicator', padTop=-2, height=7, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, icon='ui_81_64_2', ignoreSize=True)
        chargeIndicator.rectWidth = 44
        chargeIndicator.rectHeight = 7
        self.sr.underlay = underlay
        self.sr.chargeIndicator = chargeIndicator
        self.sr.flagIcon = icon
        self.sr.groupMark = groupMark




