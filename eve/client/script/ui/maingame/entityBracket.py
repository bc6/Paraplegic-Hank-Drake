import uicls
import uiconst
import uthread
import blue
import util
import math
import uiutil
import trinity
COLOR_BRACKET = (252 / 255.0, 223 / 255.0, 192 / 255.0)

class EntityBracket(uicls.BoundingBoxBracket):
    __guid__ = 'uicls.EntityBracket'
    __notifyevents__ = ['OnEntityBracketShowActions']
    default_state = uiconst.UI_HIDDEN
    default_opacity = 0.0
    default_minWidth = 50
    default_minHeight = 35
    default_maxWidth = 0.0
    default_maxHeight = 0.0
    default_padLeft = -100
    default_padRight = -100

    def ApplyAttributes(self, attributes):
        uicls.BoundingBoxBracket.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.entity = attributes.entity
        self.hideThread = None
        self.animButtonsThread = None
        self.animTreeThread = None
        self.treeCont = None
        self.updateThread = None
        self.mainCont = uicls.Container(name='mainCont', parent=self)
        self.buttonCont = uicls.Container(name='buttonCont', parent=self.mainCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        rotation = 0.0
        self.cornersCont = uicls.Container(name='cornersCont', parent=self.mainCont, state=uiconst.UI_NORMAL, padLeft=100, padRight=100)
        self.cornersCont.OnMouseEnter = self.OnMouseEnter
        self.cornersCont.OnMouseExit = self.OnMouseExit
        self.cornersCont.OnMouseDown = self.OnMouseDown
        self.cornersCont.OnMouseUp = self.OnMouseUp
        self.cornersCont.OnMouseMove = self.OnMouseMove
        self.cornersCont.OnClick = self.OnClick
        self.cornersCont.GetMenu = self.GetMenu
        self.cornersCont.cursor = uiconst.UICURSOR_SELECT
        for align in (uiconst.TOPLEFT,
         uiconst.BOTTOMLEFT,
         uiconst.BOTTOMRIGHT,
         uiconst.TOPRIGHT):
            s = uicls.Sprite(name='bracketCorner', texturePath='res:/UI/Texture/Classes/EntityBracket/bracketCorner.png', parent=self.cornersCont, align=align, pos=(-10, -10, 32, 32), state=uiconst.UI_DISABLED, color=COLOR_BRACKET)
            s.texture.useTransform = True
            s.texture.rotation = rotation
            rotation += math.pi / 2

        self.treeCont = uicls.Container(name='treeCont', parent=self, state=uiconst.UI_DISABLED)



    def Close(self):
        uicls.BoundingBoxBracket.Close(self)
        self.cornersCont.OnMouseEnter = None
        self.cornersCont.OnMouseExit = None
        self.cornersCont.OnMouseDown = None
        self.cornersCont.OnMouseUp = None
        self.cornersCont.OnMouseMove = None
        self.cornersCont.OnClick = None
        self.cornersCont.GetMenu = None



    def OnMouseEnter(self, *args):
        if self.hideThread:
            self.hideThread.kill()
            self.hideThread = None
        if self.updateThread:
            self.updateThread.kill()
        self.updateThread = uthread.new(self.UpdateThread)
        self.updateThread.context = 'EntityBracket::UpdateThread'
        if self.buttonCont.state == uiconst.UI_DISABLED:
            self.ShowActions()
        self.AnimBlinkCornersIn()



    def ShowActions(self):
        self.buttonCont.Flush()
        self.buttonCont.opacity = 1.0
        self.buttonCont.state = uiconst.UI_NORMAL
        self.padBottom = self.padTop = 0
        self.SetOrder(0)
        btnOffsetY = 45
        btnOffsetX = 20
        aoSvc = sm.GetService('actionObjectClientSvc')
        actionList = aoSvc.GetActionList(session.charid, self.entity.entityID)
        isMultiAction = len(actionList) > 1
        (l, t, w, h,) = self.GetAbsolute()
        y = t + h / 2
        isAtTop = y > uicore.desktop.height / 2
        align = (uiconst.CENTERBOTTOM, uiconst.CENTERTOP)[isAtTop]
        self.buttonCont.height = 50
        i = 0
        for (actionID, (label, isEnabled, trash,),) in actionList.iteritems():
            isAtLeft = (i + 1 + isAtTop + len(actionList)) % 2
            if isMultiAction:
                button = ActionObjectButton(parent=self.buttonCont, align=align, top=i * btnOffsetY, func=self.OnButtonClicked, actionID=actionID, text=label, isEnabled=isEnabled, isReversed=isAtLeft, scalingCenter=(isAtLeft, float(not isAtTop)), opacity=0.0)
                self.buttonCont.state = uiconst.UI_NORMAL
                leftAbs = (1, -1)[isAtLeft]
                button.left = (btnOffsetX + button.width / 2) * leftAbs
                self.buttonCont.height += btnOffsetY
            else:
                button = uicls.ActionObjectLabel(parent=self.buttonCont, align=align, top=30, text=label, isEnabled=isEnabled, opacity=0.0, actionID=actionID)
                self.buttonCont.state = uiconst.UI_DISABLED
            i += 1

        if isAtTop:
            self.buttonCont.align = uiconst.TOTOP
            self.padTop = -self.buttonCont.height
        else:
            self.buttonCont.align = uiconst.TOBOTTOM
            self.padBottom = -self.buttonCont.height
        self.animButtonsThread = uthread.new(self.AnimShowButtons)
        self.treeCont.Flush()
        if isMultiAction:
            self.animTreeThread = uthread.new(self.AnimShowTree, isAtTop, btnOffsetX, btnOffsetY)
        sm.ScatterEvent('OnEntityBracketShowActions', self)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_CLICK, self.OnGlobalMouseClick)



    def AnimShowButtons(self):
        buttons = self.buttonCont.children[:]
        buttons.reverse()
        for b in buttons:
            uicore.animations.FadeIn(b, duration=0.3)
            blue.synchro.SleepWallclock(50)




    def AnimShowTree(self, isAtTop, btnOffsetX, btnOffsetY):
        longLineHeight = 80
        hexHeight = 14
        linePad = 5
        numButtons = len(self.buttonCont.children)
        align = [uiconst.CENTERBOTTOM, uiconst.CENTERTOP][isAtTop]
        itemAlign = [uiconst.TOTOP, uiconst.TOBOTTOM][isAtTop]
        lineTexturePaths = ('res:/UI/Texture/Classes/EntityBracket/line1.png', 'res:/UI/Texture/Classes/EntityBracket/line2.png')
        longLineTexture = ('res:/UI/Texture/Classes/EntityBracket/longLineBottom.png', 'res:/UI/Texture/Classes/EntityBracket/longLineTop.png')[isAtTop]
        height = numButtons * btnOffsetY + longLineHeight + hexHeight / 2
        if not isAtTop:
            height -= btnOffsetY
        treeMainCont = uicls.Container(parent=self.treeCont, align=align, width=2 * btnOffsetX, height=height)
        longLine = uicls.Sprite(parent=treeMainCont, texturePath=longLineTexture, align=itemAlign, color=COLOR_BRACKET, height=longLineHeight, padLeft=linePad, padRight=linePad)
        longLine.opacity = 0.0
        for (i, b,) in enumerate(self.buttonCont.children):
            hexCont = uicls.Container(parent=treeMainCont, align=itemAlign, height=hexHeight)
            hexColor = util.Color(*COLOR_BRACKET).SetAlpha(0.4).GetRGBA()
            hexLeft = (1, -1)[((isAtTop + i) % 2)] * btnOffsetX
            uicls.Sprite(parent=hexCont, texturePath='res:/UI/Texture/Classes/EntityBracket/hex.png', color=hexColor, align=uiconst.CENTER, pos=(hexLeft,
             0,
             hexHeight,
             hexHeight), padding=-2)
            if i != numButtons - 1:
                line = uicls.Sprite(parent=treeMainCont, texturePath=lineTexturePaths[(i % 2)], align=itemAlign, color=COLOR_BRACKET, height=btnOffsetY - hexHeight, padLeft=linePad, padRight=linePad)

        for c in treeMainCont.children:
            c.opacity = 0.0

        for c in treeMainCont.children:
            uicore.animations.FadeIn(c, duration=0.8)
            blue.synchro.SleepWallclock(100)




    def OnEntityBracketShowActions(self, entityBracket):
        if entityBracket != self:
            self.AnimFadeOut()



    def OnButtonClicked(self, actionID):
        self.AnimFadeOut()
        aoSvc = sm.GetService('actionObjectClientSvc')
        aoSvc.TriggerActionOnObject(session.charid, self.entity.entityID, actionID)



    def OnMouseExit(self, *args):
        if self.hideThread:
            self.hideThread.kill()
        self.hideThread = uthread.new(self.HideThread)
        if self.updateThread:
            self.updateThread.kill()
            self.updateThread = None



    def HideThread(self):
        while True:
            blue.pyos.synchro.SleepWallclock(2000)
            if not uiutil.IsUnder(uicore.uilib.mouseOver, self):
                break

        self.AnimFadeOut()



    def UpdateThread(self):
        while True:
            blue.pyos.synchro.SleepWallclock(250)
            aoSvc = sm.GetService('actionObjectClientSvc')
            actionList = aoSvc.GetActionList(session.charid, self.entity.entityID)
            for b in self.buttonCont.children:
                if hasattr(b, 'SetEnabled'):
                    b.SetEnabled(actionList[b.actionID][1])





    def OnMouseDown(self, button, *args):
        sm.GetService('mouseInput').OnMouseDown(button, uicore.uilib.x, uicore.uilib.y, self.entity.entityID)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)



    def OnMouseUp(self, button, *args):
        sm.GetService('mouseInput').OnMouseUp(button, uicore.uilib.x, uicore.uilib.y, self.entity.entityID)



    def OnGlobalMouseUp(self, *args):
        if not uiutil.IsUnder(uicore.uilib.mouseOver, self):
            self.OnMouseExit()



    def OnGlobalMouseClick(self, *args):
        if not uiutil.IsUnder(uicore.uilib.mouseOver, self):
            uthread.new(self.AnimFadeOut)



    def OnMouseMove(self, *args):
        sm.GetService('mouseInput').OnMouseMove(uicore.uilib.dx, uicore.uilib.dy, self.entity.entityID)



    def AnimBlinkCornersIn(self, sleep = False):
        self.StopAnimations()
        self.opacity = 1.0
        uicore.animations.FadeTo(obj=self.cornersCont, startVal=0.0, endVal=1.0, duration=0.1, loops=4, sleep=sleep)



    def AnimFadeOut(self):
        self.buttonCont.state = uiconst.UI_DISABLED
        uicore.animations.FadeOut(self, duration=0.3, sleep=True)



    def OnClick(self, *args):
        aoSvc = sm.GetService('actionObjectClientSvc')
        aoSvc.TriggerDefaultActionOnObject(session.charid, self.entity.entityID)



    def GetMenu(self):
        return sm.GetService('contextMenuClient').GetMenuForEntityID(self.entity.entityID)



    def SetActive(self, *args):
        self.treeCont.Flush()
        self.buttonCont.Flush()
        uthread.new(self.AnimSetActive)



    def AnimSetActive(self, *args):
        self.state = uiconst.UI_PICKCHILDREN
        self.opacity = 1.0
        self.AnimBlinkCornersIn(sleep=True)
        blue.synchro.SleepWallclock(2000)
        if not uiutil.IsUnder(uicore.uilib.mouseOver, self):
            self.AnimFadeOut()



    def SetInactive(self, *args):
        uthread.new(self._SetInactive)



    def _SetInactive(self):
        self.AnimFadeOut()
        self.state = uiconst.UI_HIDDEN




class ActionObjectLabel(uicls.Container):
    __guid__ = 'uicls.ActionObjectLabel'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_DISABLED
    default_height = 16

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        text = attributes.text
        self.isEnabled = attributes.isEnabled
        self.actionID = attributes.actionID
        if self.isEnabled:
            color = COLOR_BRACKET
        else:
            color = (142 / 255.0,
             122 / 255.0,
             101 / 255.0,
             1.0)
        self.label = uicls.Label(parent=self, align=uiconst.CENTER, text=text, top=1, fontsize=16, color=color)
        self.width = max(self.label.width + 40, 130)




class ActionObjectButton(uicls.Transform):
    __guid__ = 'uicls.ActionObjectButton'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_scale = (1.0, 1.0)
    default_scalingCenter = (1.0, 0.5)
    default_height = 35
    default_isReversed = False
    GRADIENT_ALPHA_DISABLED = 0.1
    GRADIENT_ALPHA_IDLE = 0.3
    GRADIENT_ALPHA_HOVER = 0.7
    GRADIENT_ALPHA_MOUSEDOWN = 0.9
    WEDGE_TOP = -4

    def ApplyAttributes(self, attributes):
        uicls.Transform.ApplyAttributes(self, attributes)
        text = attributes.text
        self.func = attributes.func
        self.actionID = attributes.actionID
        self.isEnabled = attributes.isEnabled
        isReversed = attributes.get('isReversed', self.default_isReversed)
        color = COLOR_BRACKET
        colorGradient = util.Color(*color).SetBrightness(0.4).SetAlpha(self.GRADIENT_ALPHA_IDLE).GetRGBA()
        colorEdges = util.Color(*color).SetBrightness(0.5).GetRGBA()
        self.mainTransform = uicls.Transform(name='mainTransform', parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5), scale=((1, -1)[isReversed], 1.0))
        topCont = uicls.Container(name='topCont', parent=self.mainTransform, align=uiconst.TOTOP, height=5, state=uiconst.UI_DISABLED)
        uicls.Sprite(name='topGradientLeft', parent=topCont, texturePath='res:/UI/Texture/Classes/EntityBracket/topGradientLeft.png', align=uiconst.TOLEFT, width=57, color=colorEdges)
        uicls.Sprite(name='topWedge', parent=topCont, texturePath='res:/UI/Texture/Classes/EntityBracket/topWedge.png', align=uiconst.TORIGHT, width=55, color=colorEdges)
        uicls.Sprite(name='topMiddle', parent=topCont, texturePath='res:/UI/Texture/Classes/EntityBracket/topMiddle.png', align=uiconst.TOALL, color=colorEdges)
        self.wedge = uicls.Sprite(name='wedge', parent=topCont, texturePath='res:/UI/Texture/Classes/EntityBracket/wedge.png', align=uiconst.TOPRIGHT, pos=(11,
         self.WEDGE_TOP,
         33,
         4), color=color)
        bottomCont = uicls.Container(name='bottomCont', parent=self.mainTransform, align=uiconst.TOBOTTOM, height=4, state=uiconst.UI_DISABLED)
        uicls.Sprite(name='bottomWedgeLeft', parent=bottomCont, texturePath='res:/UI/Texture/Classes/EntityBracket/bottomWedgeLeft.png', align=uiconst.TOLEFT, width=57, color=colorEdges)
        uicls.Sprite(name='bottom', parent=bottomCont, texturePath='res:/UI/Texture/Classes/EntityBracket/bottom.png', align=uiconst.TOALL, color=colorEdges)
        self.gradient = uicls.Container(name='gradientCont', parent=self.mainTransform, state=uiconst.UI_DISABLED, padTop=-3, padBottom=-3)
        gradientTopCont = uicls.Container(name='gradientTopCont', align=uiconst.TOTOP, parent=self.gradient, height=4)
        uicls.Sprite(name='gradientTopWedge', parent=gradientTopCont, texturePath='res:/UI/Texture/Classes/EntityBracket/gradientTopWedge.png', align=uiconst.TORIGHT, width=55, color=colorGradient)
        uicls.Sprite(name='gradientTop', parent=gradientTopCont, texturePath='res:/UI/Texture/Classes/EntityBracket/gradientTop.png', align=uiconst.TOALL, color=colorGradient)
        gradientBottomCont = uicls.Container(name='gradientBottomCont', align=uiconst.TOBOTTOM, parent=self.gradient, height=3)
        uicls.Sprite(name='gradientBottomWedge', parent=gradientBottomCont, texturePath='res:/UI/Texture/Classes/EntityBracket/gradientBottomWedge.png', align=uiconst.TOLEFT, width=57, color=colorGradient)
        uicls.Sprite(name='gradientBottom', parent=gradientBottomCont, texturePath='res:/UI/Texture/Classes/EntityBracket/gradientBottom.png', align=uiconst.TOALL, color=colorGradient)
        uicls.Sprite(name='gradientTopWedge', parent=self.gradient, texturePath='res:/UI/Texture/Classes/EntityBracket/gradientMiddle.png', align=uiconst.TOALL, color=colorGradient)
        self.label = uicls.Label(parent=self, align=uiconst.CENTER, text=text, top=1, fontsize=16, color=color)
        self.width = max(self.label.width + 60, 150)
        if not self.isEnabled:
            self.mainTransform.opacity = self.label.opacity = 0.2



    def OnClick(self, *args):
        if not self.isEnabled:
            return 
        uicore.animations.Tr2DScaleTo(self, self.scale, (0.0, 0.0), duration=1.5)
        self.func(self.actionID)



    def OnMouseEnter(self, *args):
        if not self.isEnabled:
            return 
        self.SetSelected()
        uicore.animations.MorphScalar(self.wedge, 'top', self.WEDGE_TOP, 0, duration=0.2)
        if not self.parent:
            return 
        for c in self.parent.children:
            if c != self:
                c.ScaleOut()




    def SetSelected(self):
        if not self.isEnabled:
            return 
        uicore.animations.FadeTo(self.gradient, self.gradient.opacity, self.GRADIENT_ALPHA_HOVER, duration=0.3)



    def SetEnabled(self, enabled):
        if self.isEnabled != enabled:
            self.isEnabled = enabled
            endVal = 1.0
            if not enabled:
                endVal = 0.2
            self.StopAnimations()
            uicore.animations.FadeTo(self.mainTransform, endVal, duration=0.3)
            uicore.animations.FadeTo(self.label, endVal, duration=0.3)



    def OnMouseExit(self, *args):
        if not self.isEnabled:
            return 
        self.SetDeselected()
        uicore.animations.MorphScalar(self.wedge, 'top', 0, self.WEDGE_TOP, duration=0.1)
        if not self.parent:
            return 
        for c in self.parent.children:
            if c != self:
                c.SetDeselected()
                c.ScaleIn()

        if self.parent:
            self.parent.OnMouseExit(self, *args)



    def SetDeselected(self):
        uicore.animations.FadeTo(self.gradient, self.gradient.opacity, self.GRADIENT_ALPHA_IDLE, duration=0.3)



    def ScaleIn(self):
        self.StopAnimations()
        uicore.animations.Tr2DScaleTo(self, self.scale, (1.0, 1.0), duration=0.3)
        uicore.animations.FadeTo(self, self.opacity, 1.0, duration=0.3)



    def ScaleOut(self):
        self.StopAnimations()
        uicore.animations.Tr2DScaleTo(self, self.scale, (0.95, 0.95), duration=0.3)
        uicore.animations.FadeTo(self, self.opacity, 0.3, duration=0.3)




