import blue
import trinity
import uicls
import uiconst
import uthread
import uiutil
import util
import math
import random
TIME_BASE = 0.3

class ScreenWedgeBracketTop(uicls.Transform):
    __guid__ = 'uicls.ScreenWedgeBracketTop'
    default_name = 'ScreenWedgeBracketTop'
    default_hasCorners = True
    default_wedgeWidth = 100
    default_wedgeTopStart = -10
    default_wedgePosRatio = 0.5
    default_align = uiconst.TOTOP
    default_height = 25
    default_rotation = 0.0

    def ApplyAttributes(self, attributes):
        global TIME_BASE
        uicls.Transform.ApplyAttributes(self, attributes)
        TIME_BASE = 0.3
        self.hasCorners = attributes.get('hasCorners', self.default_hasCorners)
        wedgeWidth = attributes.get('wedgeWidth', self.default_wedgeWidth)
        wedgeTopStart = attributes.get('wedgeTopStart', self.default_wedgeTopStart)
        self.wedgePosRatio = attributes.get('wedgePosRatio', self.default_wedgePosRatio)
        self.borderLeft = uicls.Frame(parent=self, name='borderLeft', texturePath='res:/UI/Texture/classes/CQMainScreen/borderLeft.png', cornerSize=16, align=uiconst.TOPLEFT, pos=(0, 1, 200, 48), padLeft=2, color=util.Color.WHITE)
        self.wedge = uicls.Frame(parent=self, name='wedge', texturePath='res:/UI/Texture/classes/CQMainScreen/wedge.png', cornerSize=13, align=uiconst.TOPLEFT, pos=(300,
         wedgeTopStart,
         wedgeWidth,
         27), padding=(-5, 0, -5, 0), color=util.Color.WHITE)
        self.borderRight = uicls.Frame(parent=self, name='borderLeft', texturePath='res:/UI/Texture/classes/CQMainScreen/borderRight.png', cornerSize=16, align=uiconst.TOPRIGHT, pos=(0, 1, 200, 48), padRight=2, color=util.Color.WHITE)
        if self.hasCorners:
            self.cornerLeft = uicls.Sprite(parent=self, name='cornerLeft', texturePath='res:/UI/Texture/classes/CQMainScreen/cornerLeft.png', pos=(0, 0, 22, 22))
            self.cornerRight = uicls.Sprite(parent=self, name='cornerRight', texturePath='res:/UI/Texture/classes/CQMainScreen/cornerRight.png', pos=(0, 0, 22, 22), align=uiconst.TOPRIGHT)



    def _OnResize(self):
        if not hasattr(self, 'wedge'):
            return 
        self.UpdatePosition()



    def UpdatePosition(self):
        (w, h,) = self.GetAbsoluteSize()
        self.wedge.left = (w - self.wedge.width) * self.wedgePosRatio
        self.borderLeft.width = self.wedge.left
        self.borderRight.width = w - self.wedge.left - self.wedge.width



    def AnimAppear(self):
        if self.hasCorners:
            uicore.animations.FadeIn(self.cornerLeft, duration=TIME_BASE / 3, loops=3)
            uicore.animations.FadeIn(self.cornerRight, duration=TIME_BASE / 3, loops=3, sleep=True)
        uicore.animations.FadeIn(self.borderLeft, duration=TIME_BASE)
        uicore.animations.FadeIn(self.borderRight, duration=TIME_BASE)
        uicore.animations.FadeIn(self.wedge, duration=TIME_BASE / 3, loops=3, sleep=True)
        uicore.animations.MorphScalar(self.wedge, 'top', self.wedge.top, 0, duration=TIME_BASE, curveType=uiconst.ANIM_LINEAR, sleep=True)



    def AnimDisappear(self):
        uicore.animations.FadeOut(self)




class ScreenWedgeBracketBottom(ScreenWedgeBracketTop):
    __guid__ = 'uicls.ScreenWedgeBracketBottom'
    default_name = 'ScreenWedgeBracketBottom'
    default_align = uiconst.TOBOTTOM
    default_rotation = math.pi


class ScreenSimpleBracketTop(uicls.Frame):
    __guid__ = 'uicls.ScreenSimpleBracketTop'
    default_name = 'ScreenSimpleBracketTop'
    default_texturePath = 'res:/UI/Texture/classes/CQMainScreen/simpleBracketTop.png'
    default_cornerSize = 21
    default_align = uiconst.TOTOP
    default_height = 21
    default_color = util.Color.WHITE

    def AnimAppear(self):
        uicore.animations.FadeIn(self, duration=TIME_BASE)



    def AnimDisappear(self):
        uicore.animations.FadeOut(self, duration=TIME_BASE)




class ScreenSimpleBracketBottom(ScreenSimpleBracketTop):
    __guid__ = 'uicls.ScreenSimpleBracketBottom'
    default_name = 'ScreenSimpleBracketTop'
    default_texturePath = 'res:/UI/Texture/classes/CQMainScreen/simpleBracketBottom.png'
    default_align = uiconst.TOBOTTOM


class ScreenFrameBase(uicls.Container):
    __guid__ = 'uicls._ScreenFrameBase'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.bracketLayer = uicls.Container(name='bracketCont', parent=self)
        self.mainCont = uicls.Container(name='mainCont', parent=self)
        self.topBracket = None
        self.bottomBracket = None
        uthread.new(self.AnimAppear)



    def AnimAppear(self):
        (w, h,) = self.GetAbsoluteSize()
        uicore.animations.MorphScalar(self.topBracket, 'padTop', h / 2, 0, duration=TIME_BASE)
        uicore.animations.MorphScalar(self.bottomBracket, 'padBottom', h / 2, 0, duration=TIME_BASE, sleep=True)
        for obj in self.bracketLayer.children:
            uthread.new(obj.AnimAppear)
            blue.pyos.synchro.Sleep(200)

        blue.pyos.synchro.Sleep(2000)
        for c in self.mainCont.children:
            if hasattr(c, 'AnimAppear'):
                uthread.new(c.AnimAppear)





class ScreenFrame1(ScreenFrameBase):
    __guid__ = 'uicls.ScreenFrame1'
    default_name = 'ScreenFrame1'

    def ApplyAttributes(self, attributes):
        uicls._ScreenFrameBase.ApplyAttributes(self, attributes)
        self.bottomBracket = uicls.ScreenWedgeBracketBottom(parent=self.bracketLayer, wedgePosRatio=0.3, rotation=math.pi, align=uiconst.TOBOTTOM)
        self.topBracket = uicls.ScreenWedgeBracketTop(parent=self.bracketLayer, wedgePosRatio=0.3, rotation=0)




class ScreenFrame2(ScreenFrameBase):
    __guid__ = 'uicls.ScreenFrame2'
    default_name = 'ScreenFrame2'

    def ApplyAttributes(self, attributes):
        ScreenFrameBase.ApplyAttributes(self, attributes)
        self.topBracket = uicls.ScreenWedgeBracketTop(parent=self.bracketLayer, wedgePosRatio=0.3, wedgeWidth=200, hasCorners=False)
        self.bottomBracket = uicls.ScreenSimpleBracketBottom(parent=self.bracketLayer)




class ScreenFrame3(ScreenFrameBase):
    __guid__ = 'uicls.ScreenFrame3'
    default_name = 'ScreenFrame3'

    def ApplyAttributes(self, attributes):
        ScreenFrameBase.ApplyAttributes(self, attributes)
        self.topBracket = uicls.ScreenSimpleBracketTop(parent=self.bracketLayer)
        self.bottomBracket = uicls.ScreenWedgeBracketBottom(parent=self.bracketLayer, wedgePosRatio=0.3, wedgeWidth=200, hasCorners=False)




class ScreenFrame4(ScreenFrameBase):
    __guid__ = 'uicls.ScreenFrame4'
    default_name = 'ScreenFrame4'

    def ApplyAttributes(self, attributes):
        ScreenFrameBase.ApplyAttributes(self, attributes)
        self.topBracket = uicls.ScreenSimpleBracketTop(parent=self.bracketLayer)
        self.bottomBracket = uicls.ScreenSimpleBracketBottom(parent=self.bracketLayer)




class ScreenFrame5(ScreenFrame1):
    __guid__ = 'uicls.ScreenFrame5'
    default_name = 'ScreenFrame5'

    def ApplyAttributes(self, attributes):
        ScreenFrame1.ApplyAttributes(self, attributes)
        ScreenBlinkingSquares(parent=self.bracketLayer, padLeft=50, padBottom=-5, padRight=15)




class ScreenHeading1(uicls.Container):
    __guid__ = 'uicls.ScreenHeading1'
    default_name = 'ScreenHeading1'
    default_align = uiconst.TOTOP
    default_fillColor = (0.180392157, 0.219607843, 0.239215686, 1.0)
    default_gradientColor = (0.152941176, 0.168627451, 0.17254902, 1.0)
    default_leftContWidth = 60
    default_height = 60

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        fillColor = attributes.get('fillColor', self.default_fillColor)
        gradientColor = attributes.get('gradientColor', self.default_gradientColor)
        leftContWidth = attributes.get('leftContWidth', self.default_leftContWidth)
        appear = attributes.get('appear', False)
        self.leftCont = uicls.Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=leftContWidth)
        uicls.Fill(name='leftBg', bgParent=self.leftCont, color=fillColor)
        self.mainCont = uicls.Container(name='mainCont', parent=self, padLeft=0, padRight=0)
        gradient = uicls.Sprite(name='rightGradient', bgParent=self.mainCont, color=gradientColor, texturePath='res:/UI/Texture/classes/CQMainScreen/gradientHoriz.png')
        if appear:
            uthread.new(self.AnimAppear)
        else:
            self.opacity = 0.0



    def AnimAppear(self):
        TIME_BASE = 0.2
        (w, h,) = self.GetAbsoluteSize()
        self.opacity = 1.0
        uicore.animations.MorphScalar(self.leftCont, 'displayWidth', 0, self.leftCont.width, duration=TIME_BASE)
        uicore.animations.FadeIn(self.leftCont, duration=TIME_BASE / 3, loops=3, sleep=True)
        uicore.animations.MorphScalar(self.mainCont, 'displayWidth', 0, w - self.leftCont.width, duration=TIME_BASE)
        uicore.animations.FadeIn(self.mainCont, duration=TIME_BASE / 3, loops=3, sleep=True)




class ScreenHeading2(uicls.Container):
    __guid__ = 'uicls.ScreenHeading2'
    default_name = 'ScreenHeading2'
    default_height = 60
    default_width = 600
    default_align = uiconst.TOPLEFT
    default_text = ''
    default_opacity = 0.0
    default_hasBargraph = True

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        text = attributes.get('text', self.default_text)
        appear = attributes.get('appear', False)
        self.hasBargraph = attributes.get('hasBargraph', self.default_hasBargraph)
        rightCont = uicls.Container(name='rightCont', parent=self, align=uiconst.TORIGHT, width=446, padBottom=5)
        uicls.Sprite(name='rightGraphics', parent=rightCont, align=uiconst.TOBOTTOM, texturePath='res:/UI/Texture/classes/CQMainScreen/heading2.png', height=14)
        uicls.Fill(name='thickLine', parent=self, align=uiconst.TOBOTTOM, height=6, padBottom=9, color=util.Color.WHITE)
        self.label = uicls.Label(parent=self, text=text, top=10, fontsize=30, color=util.Color.WHITE)
        self.movingFill = uicls.Fill(name='movingFill', parent=self, align=uiconst.BOTTOMRIGHT, pos=(0, 0, 100, 3), color=util.Color.WHITE)
        if self.hasBargraph:
            barGraphCont = uicls.Container(name='bargraphCont', parent=self, align=uiconst.TOPRIGHT, pos=(10, 8, 332, 31))
            self.barGraph = uicls.Sprite(name='barGraph', parent=barGraphCont, texturePath='res:/UI/Texture/classes/CQMainScreen/barGraph.png', align=uiconst.CENTER, width=barGraphCont.width, height=31)
            self.barGraph.color.a = 0.6
        if appear:
            uthread.new(self.AnimAppear)



    def AnimAppear(self):
        TIME_BASE = 0.2
        uicore.animations.FadeIn(self, duration=TIME_BASE / 3, loops=3)
        uicore.animations.MorphScalar(self.movingFill, 'left', 0, 244, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE, duration=2.0)
        if self.hasBargraph:
            uicore.animations.MorphScalar(self.barGraph, 'height', 0, 45, curveType=uiconst.ANIM_RANDOM, duration=1.0)




class ScreenHeading3(uicls.Container):
    __guid__ = 'uicls.ScreenHeading3'
    default_name = 'ScreenHeading3'
    default_height = 60
    default_width = 600
    default_align = uiconst.TOPLEFT
    default_text = ''
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        text = attributes.get('text', self.default_text)
        appear = attributes.get('appear', False)
        self.label = uicls.Label(parent=self, align=uiconst.CENTER, fontsize=self.height - 25, text=text)
        uicls.Fill(bgParent=self, color=(0.5, 0.5, 0.5, 1.0))
        if appear:
            uthread.new(self.AnimAppear)



    def AnimAppear(self):
        uicore.animations.BlinkIn(self, sleep=True)
        uicore.animations.BlinkIn(self.label, sleep=True)
        uicore.animations.MorphScalar(self.label, 'opacity', startVal=1.0, endVal=0.5, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)




class ScreenBlinkingSquares(uicls.Container):
    __guid__ = 'uicls.ScreenBlinkingSquares'
    default_name = 'ScreenBlinkingSquares'
    default_height = 10
    default_align = uiconst.TOBOTTOM
    default_opacity = 0.0
    default_padBottom = 10
    default_padLeft = 10
    default_padRight = 10

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        left1 = uicls.Fill(name='left1', parent=self, align=uiconst.TOLEFT, width=8, padBottom=5, color=util.Color.WHITE)
        left2 = uicls.Fill(name='left2', parent=self, align=uiconst.TOLEFT, width=30, padLeft=3, color=util.Color.WHITE)
        left3 = uicls.Fill(name='left3', parent=self, align=uiconst.TOLEFT, width=8, padLeft=3, color=util.Color.WHITE)
        self.label = uicls.Label(parent=self, align=uiconst.TOLEFT, width=100, padLeft=5, fontsize=9)
        self.right1 = uicls.Fill(name='right1', parent=self, align=uiconst.TORIGHT, width=50, color=util.Color.WHITE)
        self.right2 = uicls.Fill(name='right2', parent=self, align=uiconst.TORIGHT, width=50, color=util.Color.WHITE, padRight=3)
        self.right3 = uicls.Fill(name='right3', parent=self, align=uiconst.TORIGHT, width=50, color=util.Color.WHITE, padRight=3)



    def AnimAppear(self):
        TIME_BASE = 0.2
        uicore.animations.FadeIn(self, duration=TIME_BASE / 3, loops=3)
        uthread.new(self.UpdateBitCounter)
        uthread.new(self.UpdateText)



    def UpdateText(self):
        x1 = 10000
        x2 = 30000
        msgList = ['59 4F 55 20',
         '48 41 56 45',
         '20 57 41 59',
         '20 54 4F 4F',
         '20 4D 55 43',
         '48 20 54 49',
         '4D 45 20 4F',
         '4E 20 59 4F',
         '55 52 20 48',
         '41 4E 44 53']
        while not self.destroyed:
            for msg in msgList:
                self.label.text = '<b>%s' % msg
                uicore.animations.FadeIn(self.label, duration=TIME_BASE / 3, loops=3)
                blue.pyos.synchro.Sleep(random.randint(1000, 2000))





    def UpdateBitCounter(self):
        count = 0
        while not self.destroyed:
            val = max(0.2, count & 1)
            uicore.animations.FadeTo(self.right1, self.right1.opacity, val)
            val = max(0.2, count >> 1 & 1)
            uicore.animations.FadeTo(self.right2, self.right2.opacity, val)
            val = max(0.2, count >> 2 & 1)
            uicore.animations.FadeTo(self.right3, self.right3.opacity, val)
            count += 1
            if count == 8:
                count = 0
            blue.pyos.synchro.Sleep(1000)





class AutoTextScroll(uicls.Container):
    __guid__ = 'uicls.AutoTextScroll'
    default_name = 'AutoScrollHorizontal'
    default_scrollSpeed = 10
    default_clipChildren = True
    default_textList = None
    default_fontSize = 30
    default_fadeColor = util.Color.BLACK
    default_fadeWidth = 100
    default_color = util.Color.WHITE

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        textList = attributes.get('textList', self.default_textList)
        self.scrollSpeed = attributes.get('scrollSpeed', self.default_scrollSpeed)
        self.fontSize = attributes.get('fontSize', self.default_fontSize)
        fadeColor = attributes.get('fadeColor', self.default_fadeColor)
        fadeWidth = attributes.get('fadeWidth', self.default_fadeWidth)
        self.color = attributes.get('color', self.default_color)
        self.scrollThread = None
        if fadeColor:
            uicls.Sprite(name='leftFade', parent=self, texturePath='res:/UI/Texture/classes/CQMainScreen/autoTextGradientLeft.png', color=fadeColor, align=uiconst.TOLEFT, width=fadeWidth, state=uiconst.UI_DISABLED)
            uicls.Sprite(name='leftFade', parent=self, texturePath='res:/UI/Texture/classes/CQMainScreen/autoTextGradientRight.png', color=fadeColor, align=uiconst.TORIGHT, width=fadeWidth, state=uiconst.UI_DISABLED)
        self.textCont = uicls.Container(name='textCont', parent=self, align=uiconst.CENTERLEFT, height=self.fontSize)
        if textList:
            self.SetTextList(textList)



    def SetTextList(self, textList, funcList = None, funcKeywordsList = None):
        self.textCont.Flush()
        if self.scrollThread:
            self.scrollThread.kill()
        if not textList:
            return 
        x = 0
        for (i, text,) in enumerate(textList):
            if i != 0:
                bullet = uicls.Sprite(parent=self.textCont, align=uiconst.CENTERLEFT, texturePath='res:/UI/texture/classes/CQMainScreen/bullet.png', pos=(x,
                 0,
                 11,
                 11), color=self.color)
                bulletWidth = bullet.width + 10
            else:
                bulletWidth = 0
            if funcList:
                clickFunc = funcList[i]
            else:
                clickFunc = None
            if funcKeywordsList:
                funcKeywords = funcKeywordsList[i]
            else:
                funcKeywords = None
            labelCont = uicls._AutoTextLabelCont(parent=self.textCont, clickFunc=clickFunc, funcKeywords=funcKeywords, left=x + bulletWidth, align=uiconst.TOPLEFT)
            label = uicls.Label(parent=labelCont, text='<b>%s' % text, fontsize=self.fontSize, color=self.color)
            labelCont.width = label.width
            labelCont.height = label.height
            x += label.width + 10 + bulletWidth

        self.textCont.width = x
        self.textCont.height = label.height
        self.scrollThread = uthread.new(self.ScrollThread)



    def ScrollThread(self):
        (w, h,) = self.GetAbsoluteSize()
        self.textCont.left = w
        while not self.destroyed:
            duration = self.textCont.width / float(self.scrollSpeed)
            uicore.animations.MorphScalar(self.textCont, 'left', startVal=w, endVal=-self.textCont.width, duration=duration, curveType=uiconst.ANIM_LINEAR, sleep=True)





class LabelCont(uicls.Container):
    __guid__ = 'uicls._AutoTextLabelCont'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.hoverFill = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.0), padLeft=-5, padRight=-5)
        self.clickFunc = attributes.get('clickFunc', None)
        self.funcKeywords = attributes.get('funcKeywords', None)



    def OnMouseEnter(self, *args):
        if self.clickFunc:
            uicore.animations.FadeIn(self.hoverFill, endVal=0.5)



    def OnMouseExit(self, *args):
        if self.clickFunc:
            uicore.animations.FadeOut(self.hoverFill)



    def OnClick(self, *args):
        if self.clickFunc:
            if self.funcKeywords:
                self.clickFunc(**self.funcKeywords)
            else:
                self.clickFunc()




class TextBanner(uicls.Container):
    __guid__ = 'uicls.TextBanner'
    default_height = 80
    default_align = uiconst.TOBOTTOM
    default_leftContWidth = 0
    default_scrollText = True
    default_fontSize = 30
    default_color = (0.15, 0.15, 0.15, 1.0)

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        text = attributes.get('text', '')
        fontSize = attributes.get('fontSize', self.default_fontSize)
        leftContWidth = attributes.get('leftContWidth', self.default_leftContWidth)
        color = attributes.get('color', self.default_color)
        self.leftCont = uicls.Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=leftContWidth)
        autoText = uicls.AutoTextScroll(parent=self, align=uiconst.TOALL, scrollSpeed=70, fontSize=fontSize, textList=[text], fadeColor=color, padTop=12, padBottom=12)
        uicls.Sprite(bgParent=self, texturePath='res:/UI/Texture/Classes/CQMainScreen/autoTextGradientLeft.png', color=color)




