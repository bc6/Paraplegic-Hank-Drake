import uicls
import uiconst
import blue
import base
import util
import trinity
SEVERITY_HQ = 1
SEVERITY_ASSAULT = 2
SEVERITY_VANGUARD = 3
SEVERITY_STAGING = 4
SEVERITY = {SEVERITY_STAGING: util.KeyVal(icon='ui_94_64_6', hint=mls.UI_SHARED_INCURSION_HUD_HINT_STAGING, subTitle=mls.UI_INCURSION_SUBTITLE_STAGING),
 SEVERITY_VANGUARD: util.KeyVal(icon='ui_94_64_13', hint=mls.UI_SHARED_INCURSION_HUD_HINT_VANGUARD, subTitle=mls.UI_INCURSION_SUBTITLE_VANGUARD),
 SEVERITY_ASSAULT: util.KeyVal(icon='ui_94_64_14', hint=mls.UI_SHARED_INCURSION_HUD_HINT_ASSAULT, subTitle=mls.UI_INCURSION_SUBTITLE_ASSAULT),
 SEVERITY_HQ: util.KeyVal(icon='ui_94_64_15', hint=mls.UI_SHARED_INCURSION_HUD_HINT_HQ, subTitle=mls.UI_INCURSION_SUBTITLE_HQ)}
ARROWS = ('ui_77_32_41', 'ui_77_32_42')
EFFECT_SPACING = 16
COLOR_ENABLED = (1, 1, 1, 0.75)
COLOR_DISABLED = (1, 1, 1, 0.25)

class IncursionBossIcon(uicls.Sprite):
    __guid__ = 'uicls.IncursionBossIcon'
    default_name = 'bossIcon'
    default_texturePath = 'res:/UI/Texture/Icons/skullCrossBones10.png'
    default_state = uiconst.UI_NORMAL
    default_width = 10
    default_height = 10

    def SetBossSpawned(self, hasSawned):
        self.SetHint(mls.UI_SHARED_INCURSION_REPORT_HINT_HAS_BOSS if hasSawned else mls.UI_INCURSION_HINT_HAS_NO_BOSS)
        self.color.SetRGB(*(COLOR_ENABLED if hasSawned else COLOR_DISABLED))




class IncursionInfoContainer(uicls.NeocomContainer):
    __guid__ = 'uicls.IncursionInfoContainer'
    default_name = 'IncursionInfoContainer'
    default_state = uiconst.UI_PICKCHILDREN
    default_severity = SEVERITY_VANGUARD
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 120
    default_idx = 1
    default_collapsable = True

    def ApplyAttributes(self, attributes):
        uicls.NeocomContainer.ApplyAttributes(self, attributes)
        severity = attributes.get('severity', self.default_severity)
        influence = attributes.get('influence', 1.0)
        hasBoss = attributes.get('hasBoss', False)
        info = SEVERITY[severity]
        topContainer = uicls.Container(parent=self.content, name='topContainer', height=54, align=uiconst.TOTOP)
        self.title = uicls.Label(name='title', text='<url=localsvc:service=journal&method=ShowIncursionTab&constellationID=%d&open=1>%s</url>' % (session.constellationid, mls.UI_SHARED_INCURSION_HUD_TITLE), parent=topContainer, left=46, fontsize=14, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, letterspace=2, uppercase=True)
        self.subTitle = uicls.Label(name='subtitle', text='<b>%s</b>' % info.subTitle, parent=topContainer, top=18, left=46, fontsize=13, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, bold=True, letterspace=2, uppercase=True)
        self.severityIcon = uicls.Icon(name='severityIcon', parent=topContainer, icon=info.icon, hint=info.hint, align=uiconst.RELATIVE, color=COLOR_ENABLED, pos=(-4, -4, 48, 48), ignoreSize=True, size=48, state=uiconst.UI_NORMAL)
        self.bossIcon = uicls.IncursionBossIcon(parent=topContainer, align=uiconst.TOPRIGHT, left=18, top=2)
        self.bossIcon.SetBossSpawned(hasBoss)
        self.influenceTitle = uicls.Label(name='influenceBarLabel', text=mls.UI_SHARED_INCURSION_HUD_INFLUENCE_TITLE, parent=topContainer, align=uiconst.BOTTOMLEFT, state=uiconst.UI_NORMAL)
        self.influenceBar = uicls.SystemInfluenceBar(parent=self.content)
        bottomContainer = uicls.Container(parent=self.content, name='systemEffectCont', align=uiconst.TOTOP, height=48)
        uicls.Label(name='systemEffectsLabel', text=mls.UI_SHARED_INCURSION_HUD_SYSTEMEFFECT_TITLE, parent=bottomContainer, align=uiconst.TOPLEFT, autowidth=True, autoheight=True, state=uiconst.UI_NORMAL, top=2)
        iconParams = {'align': uiconst.RELATIVE,
         'top': 16,
         'parent': bottomContainer,
         'color': COLOR_ENABLED}
        self.effects = [uicls.Icon(name='effectIcon_cyno', icon='ui_77_32_45', hint=mls.UI_SHARED_INCURSION_SYSTEM_EFFECT_CYNO, **iconParams),
         uicls.Icon(name='effectIcon_tax', icon='ui_77_32_46', hint=mls.UI_SHARED_INCURSION_SYSTEM_EFFECT_TAX, left=(32 + EFFECT_SPACING), **iconParams),
         uicls.Icon(name='effectIcon_tank', icon='ui_77_32_43', hint=mls.UI_SHARED_INCURSION_SYSTEM_EFFECT_TANK, left=(64 + EFFECT_SPACING * 2), **iconParams),
         uicls.Icon(name='effectIcon_damage', icon='ui_77_32_44', hint=mls.UI_SHARED_INCURSION_SYSTEM_EFFECT_DAMAGE, left=(96 + EFFECT_SPACING * 3), **iconParams)]
        self.SetInfluence(influence, None, animate=False)
        self.bottomContainer = bottomContainer
        self.topContainer = topContainer
        if self.collapsed != settings.char.ui.Get('incursion_ui_collapsed', False):
            self.ToggleCollapseState()



    def SetInfluence(self, influence, positiveProgress, animate = True):
        self.influenceBar.SetInfluence(influence, positiveProgress, animate)
        if influence < 1.0:
            self.effects[2].color.SetRGB(*COLOR_ENABLED)
            self.effects[3].color.SetRGB(*COLOR_ENABLED)
        else:
            self.effects[2].color.SetRGB(*COLOR_DISABLED)
            self.effects[3].color.SetRGB(*COLOR_DISABLED)
            self.bossIcon.SetBossSpawned(True)



    def OnCollapse(self, collapsed):
        if collapsed:
            self.bottomContainer.state = uiconst.UI_HIDDEN
            self.severityIcon.state = uiconst.UI_HIDDEN
            self.subTitle.state = uiconst.UI_HIDDEN
            self.influenceTitle.state = uiconst.UI_HIDDEN
            self.title.left = 0
            self.topContainer.height = 16
            self.height = 32
        else:
            self.bottomContainer.state = uiconst.UI_PICKCHILDREN
            self.severityIcon.state = uiconst.UI_NORMAL
            self.subTitle.state = uiconst.UI_PICKCHILDREN
            self.influenceTitle.state = uiconst.UI_NORMAL
            self.title.left = 46
            self.topContainer.height = 54
            self.height = 120
        settings.char.ui.Set('incursion_ui_collapsed', collapsed)




class BarFill(uicls.Sprite):
    __guid__ = 'uicls.BarFill'
    default_name = 'BarFill'
    default_rect = (0, 0, 0, 32)
    default_texturePath = 'res:/ui/texture/classes/InfluenceBar/influenceBarDefault.png'
    default_slice = None
    default_state = uiconst.UI_HIDDEN
    default_align = uiconst.RELATIVE
    default_spriteEffect = trinity.TR2_SFX_COPY
    TEX_SIZE = 134

    def ApplyAttributes(self, attributes):
        uicls.Sprite.ApplyAttributes(self, attributes)
        slice = attributes.get('slice', self.default_slice)
        if slice is not None:
            self.SetTextureSlice(slice)



    def SetTextureSlice(self, slice):
        self.SetTexturePath(slice)



    def SetBar(self, delta):
        if not self.parent:
            return 
        (ppl, ppt, mainBarWidth, h,) = self.parent.parent.GetAbsolute()
        (pl, pt, parentWidth, h,) = self.parent.GetAbsolute()
        barOffset = pl - ppl
        self.left = int(-barOffset + mainBarWidth - round(mainBarWidth * delta))
        self.width = mainBarWidth




class SystemInfluenceBar(uicls.Container):
    __guid__ = 'uicls.SystemInfluenceBar'
    default_name = 'SystemInfluenceBar'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 12
    default_influence = 0.0
    default_align = uiconst.TOTOP
    default_padTop = 4
    default_padBottom = 4
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    FRAME_COLOR = (0.5, 0.5, 0.5, 1.0)
    TEX_WIDTH = 256
    PADDING = (0, 4, 0, 4)
    ARROW_HEIGHT = 32
    LEFT_SLICE = 'res:/ui/texture/classes/InfluenceBar/influenceBarNegative.png'
    RIGHT_SLICE = 'res:/ui/texture/classes/InfluenceBar/influenceBarPositive.png'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        (l, t, w, h,) = self.GetAbsolute()
        self.influence = attributes.get('influence', 0.0)
        self.targetInfluence = self.influence
        self.blueBar = uicls.Container(parent=self, name='blueBar', align=uiconst.TOLEFT, width=0, clipChildren=True)
        uicls.Fill(name='blueBase', parent=self.blueBar, color=(0, 0, 1, 0.25))
        self.blueArrows = uicls.BarFill(name='blueFill', pos=(0,
         0,
         w,
         h), parent=self.blueBar, color=(0, 0, 1, 0.75))
        self.knob = uicls.Line(parent=self, name='sliderKnob', color=self.FRAME_COLOR, align=uiconst.TOLEFT)
        self.redBar = uicls.Container(parent=self, name='redBar', align=uiconst.TOALL, clipChildren=True)
        uicls.Fill(name='redBase', parent=self.redBar, color=(1, 0, 0, 0.25))
        self.redArrows = uicls.BarFill(pos=(0,
         0,
         w,
         h), name='redFill', parent=self.redBar, color=(1, 0, 0, 0.75))



    def SetInfluence(self, influence, positiveProgress, animate = True):
        self.SetHint(mls.UI_INCURSION_INFLUENCE_BAR_HINT % {'influence': int(round((1.0 - influence) * 100))})
        if animate:
            self.targetInfluence = influence
            self.animationTimer = base.AutoTimer(100, self.Animation_Thread, positiveProgress)
        else:
            self.influence = self.targetInfluence = influence
            (l, t, w, h,) = self.GetAbsolute()
            totalWidth = w - self.knob.width
            self.blueBar.width = int(round(totalWidth * influence))



    def Animation_Thread(self, positiveProgress):
        (l, t, w, h,) = self.GetAbsolute()
        totalWidth = w - self.knob.width
        count = 5
        if positiveProgress is None:
            moveFunc = None
            self.blueArrows.state = uiconst.UI_HIDDEN
            self.redArrows.state = uiconst.UI_HIDDEN
        elif positiveProgress:
            moveFunc = self.MoveRight
            self.blueArrows.SetTextureSlice(self.RIGHT_SLICE)
            self.blueArrows.state = uiconst.UI_DISABLED
            self.redArrows.SetTextureSlice(self.RIGHT_SLICE)
            self.redArrows.state = uiconst.UI_DISABLED
        else:
            moveFunc = self.MoveLeft
            self.blueArrows.SetTextureSlice(self.LEFT_SLICE)
            self.blueArrows.state = uiconst.UI_DISABLED
            self.redArrows.SetTextureSlice(self.LEFT_SLICE)
            self.redArrows.state = uiconst.UI_DISABLED
        while count > 0:
            start = blue.os.GetTime()
            lastDelta = delta = 0.0
            while delta < 2.0:
                delta = max(0.0, min(blue.os.TimeDiffInMs(start) / 1000.0, 2.0))
                dt = delta - lastDelta
                if self.targetInfluence > self.influence:
                    self.influence = min(self.influence + 0.25 * dt, self.targetInfluence)
                else:
                    self.influence = max(self.influence - 0.25 * dt, self.targetInfluence)
                self.blueBar.width = int(round(totalWidth * self.influence))
                if moveFunc:
                    moveFunc(delta)
                lastDelta = delta
                blue.pyos.synchro.Yield()
                if not self or self.destroyed:
                    return 

            count -= 1

        self.animationTimer = None



    def MoveRight(self, delta):
        self.blueArrows.SetBar(2.0 - delta)
        self.redArrows.SetBar(2.0 - delta)



    def MoveLeft(self, delta):
        self.blueArrows.SetBar(delta)
        self.redArrows.SetBar(delta)




