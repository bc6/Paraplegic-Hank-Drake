import uicls
import uiconst
import util
import uiutil
import uthread
import math
import blue
import bluepy
import random
import service
import form
import localization

class MainScreen(uicls.Container):
    __guid__ = 'cqscreen.MainScreen'
    default_name = 'MainScreen'
    default_state = uiconst.UI_NORMAL
    default_opacity = 1.0
    default_align = uiconst.CENTER
    default_width = 1280
    default_height = 720

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.entityID = attributes.entityID
        self.clickFunc = None
        self.clickArgs = ()
        self.newsTicker = ScreenNewsTicker(parent=self)
        self.bottomCont = uicls.Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, height=60, state=uiconst.UI_DISABLED)
        wedgeBracket = uicls.ScreenWedgeBracketTop(parent=self.bottomCont, hasCorners=False, wedgePosRatio=0.806, wedgeWidth=30, wedgeTopStart=0, appear=True)
        self.hoverLabel = uicls.Label(name='hoverLabel', parent=self.bottomCont, align=uiconst.CENTER, fontsize=35, color=util.Color.WHITE, uppercase=True, bold=True)
        self.hoverLabel.opacity = 0.0
        self.hoverFill = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.0))
        self.mainCont = uicls.Container(name='mainCont', parent=self, state=uiconst.UI_DISABLED)
        self.mainCont.cursor = uiconst.UICURSOR_SELECT



    @bluepy.CCP_STATS_ZONE_METHOD
    def PlayTemplate(self, template, data):
        if data:
            self.clickFunc = data.get('clickFunc')
            self.clickArgs = data.get('clickArgs')
            self.hoverLabel.text = data.get('clickFuncLabel')
            if uicore.uilib.mouseOver == self.mainCont:
                uicore.animations.BlinkIn(self.hoverLabel)
        self.mainCont.Flush()
        obj = template(parent=self.mainCont, uiDesktop=self.parent, state=uiconst.UI_DISABLED)
        obj.Play(data)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetNewsTickerData(self, textList, funcList, funcKeywordsList):
        newsList = []
        for entry in textList:
            string = entry.Get('solarsystem', '')
            string += ', ' + entry.Get('region', '') if string else entry.Get('region', '')
            string = string.upper()
            string += ': ' + entry.Get('title', '') if string else entry.Get('title', '')
            newsList.append(string)

        self.newsTicker.SetNewsData(newsList, funcList, funcKeywordsList)



    def OnClick(self, *args):
        if self.clickFunc:
            if self.clickArgs:
                self.clickFunc(*self.clickArgs)
            else:
                self.clickFunc()



    def OnMouseEnter(self, *args):
        if self.clickFunc:
            uicore.animations.FadeIn(self.hoverFill, endVal=0.4, duration=0.3)
            uicore.animations.BlinkIn(self.hoverLabel)



    def OnMouseExit(self, *args):
        uicore.animations.FadeOut(self.hoverFill)
        uicore.animations.FadeOut(self.hoverLabel)



    def OnMouseDown(self, button, *args):
        sm.GetService('mouseInput').OnMouseDown(button, uicore.uilib.x, uicore.uilib.y, self.entityID)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)



    def OnGlobalMouseUp(self, *args):
        if not uiutil.IsUnder(uicore.uilib.mouseOver, self):
            self.OnMouseExit()



    def OnMouseUp(self, button, *args):
        sm.GetService('mouseInput').OnMouseUp(button, uicore.uilib.x, uicore.uilib.y, self.entityID)



    def OnMouseMove(self, *args):
        sm.GetService('mouseInput').OnMouseMove(uicore.uilib.dx, uicore.uilib.dy, self.entityID)



    def GetMenu(self):
        m = sm.GetService('contextMenuClient').GetMenuForEntityID(self.entityID)
        if session.role & service.ROLE_QA:
            m += [('QA: Reload screen', sm.GetService('holoscreen').ReloadMainScreen), ('QA: Open template test window', self._OpenMainScreenTest)]
        return m



    def _OpenMainScreenTest(self, *args):
        form.MainScreenTest.Open()




class ScreenNewsTicker(uicls.Container):
    __guid__ = 'cqscreen.ScreenNewsTicker'
    default_name = 'ScreenNewsTicker'
    default_opacity = 1.0
    default_align = uiconst.TOTOP
    default_height = 60

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        wedgeBracket = uicls.ScreenWedgeBracketBottom(parent=self, hasCorners=False, wedgePosRatio=0.85, wedgeWidth=30, wedgeTopStart=0)
        wedgeBracket.AnimAppear()
        self.leftCont = uicls.Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=200, padBottom=-20, padLeft=6)
        uicls.Sprite(name='ICLogo', parent=self.leftCont, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/CQMainScreen/ICLogo.png', pos=(30, 4, 50, 50))
        uicls.Label(name='breakingNewsLabel', parent=self.leftCont, text='A DIVISION', fontsize=25, top=5, align=uiconst.TOPLEFT, left=85, linespace=2)
        uicls.Label(name='breakingNewsLabel', parent=self.leftCont, text='OF ISD', fontsize=25, top=28, align=uiconst.TOPLEFT, left=85, linespace=2)
        uicls.Sprite(bgParent=self.leftCont, texturePath='res:/UI/Texture/classes/CQMainScreen/breakingNewsGradient.png')
        self.autoText = uicls.AutoTextScroll(parent=self, align=uiconst.TOALL, scrollSpeed=40, padBottom=-20, padLeft=-15, fadeWidth=50)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetNewsData(self, textList, funcList, funcKeywordsList):
        self.autoText.SetTextList(textList, funcList, funcKeywordsList)




class MainScreenTestWindow(uicls.Window):
    __guid__ = 'form.MainScreenTest'
    default_topParentHeight = 0
    default_fixedWidth = 1282
    default_fixedHeight = 765

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.isTabStop = True
        self.currData = None
        self.bottomCont = uicls.Container(parent=self.sr.main, align=uiconst.TOBOTTOM, height=25)
        self.mainScreen = MainScreen(parent=self.sr.main, default_align=uiconst.TOPLEFT)
        self.mainScreen.SetNewsTickerData(*sm.GetService('holoscreen').GetNewsTickerData())
        playlist = sm.GetService('holoscreen').playlist
        options = [ (cls.__guid__, (cls, dataFunc)) for (cls, dataFunc,) in playlist ]
        self.combo = uicls.Combo(parent=self.bottomCont, options=options, pos=(10, 0, 150, 0), width=150, align=uiconst.TOPLEFT, callback=self.OnCombo)
        uicls.Button(parent=self.bottomCont, label='Reload', func=self.UpdateScreen, align=uiconst.TOPLEFT, pos=(165, 0, 100, 0))
        self.checkbox = uicls.Checkbox(parent=self.bottomCont, text='Render to screen', align=uiconst.TOPLEFT, pos=(230, 0, 250, 0), checked=False, callback=self.OnCheckboxChanged)
        uicls.EveLabelMedium(parent=self.bottomCont, text='Press R to reload', align=uiconst.TOPRIGHT)
        self.checkbox.OnKeyDown = self.OnKeyDown



    def OnCheckboxChanged(self, checkbox):
        if checkbox.checked:
            self.UpdateScreen()
        else:
            sm.GetService('holoscreen').Restart()



    def UpdateScreen(self, *args):
        if not self.currData:
            return 
        if self.checkbox.checked:
            holoSvc = sm.GetService('holoscreen')
            holoSvc.StopTemplates()
            holoSvc.SetTemplates([self.currData])
            holoSvc.PlayTemplates()
        (cls, dataFunc,) = self.currData
        self.mainScreen.PlayTemplate(cls, dataFunc())



    def OnCombo(self, combo, label, data):
        self.currData = data
        self.UpdateScreen()



    def OnKeyDown(self, key, data):
        if key == uiconst.VK_R and self.currData:
            self.UpdateScreen()



    def _OnClose(self, *args):
        uthread.new(sm.GetService('holoscreen').Restart)




class CorpFinderScreen(uicls.Container):
    __guid__ = 'cqscreen.CorpFinderScreen'
    default_name = 'CorpFinderScreen'
    default_state = uiconst.UI_NORMAL
    default_opacity = 1.0
    default_align = uiconst.CENTER
    default_width = 540
    default_height = 720

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        corpID = attributes.corpID
        self.entityID = attributes.entityID
        self.cursor = uiconst.UICURSOR_SELECT
        self.hoverFill = uicls.Fill(parent=self, name='hoverFill', padding=-50, color=(1.0, 1.0, 1.0, 0.0))
        self.frame = uicls.ScreenFrame5(parent=self, align=uiconst.TOALL, padding=10)
        self.ConstructCorpLogo(corpID)
        self.hoverLabel = uicls.Label(name='hoverLabel', parent=self, text=localization.GetByLabel('UI/Station/Holoscreen/Corporation'), align=uiconst.CENTERBOTTOM, top=60, uppercase=True, fontsize=35, state=uiconst.UI_DISABLED, color=util.Color.WHITE)
        self.hoverLabel.opacity = 0.0
        self.bgSprite = uicls.Sprite(parent=self, texturePath='res:/UI/Texture/Classes/CQSideScreens/corpRecruitmentScreenBG.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=-50)
        uthread.new(self.AnimBackground)



    def ConstructCorpLogo(self, corpID):
        self.frame.mainCont.Flush()
        logo = uiutil.GetLogoIcon(name='corpLogo', parent=self.frame.mainCont, itemID=corpID, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        logo.width = logo.height = 300



    def AnimBackground(self):
        while not self.destroyed:
            loops = random.randint(1, 4)
            uicore.animations.SpGlowFadeOut(self.bgSprite, loops=loops, duration=0.4 / loops, sleep=True)
            blue.synchro.SleepWallclock(random.randint(1000, 5000))




    def OnClick(self, *args):
        sm.GetService('actionObjectClientSvc').TriggerDefaultActionOnObject(session.charid, self.entityID)



    def OnMouseDown(self, button, *args):
        sm.GetService('mouseInput').OnMouseDown(button, uicore.uilib.x, uicore.uilib.y, self.entityID)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)



    def OnGlobalMouseUp(self, *args):
        if not uiutil.IsUnder(uicore.uilib.mouseOver, self):
            self.OnMouseExit()



    def OnMouseUp(self, button, *args):
        sm.GetService('mouseInput').OnMouseUp(button, uicore.uilib.x, uicore.uilib.y, self.entityID)



    def OnMouseMove(self, *args):
        sm.GetService('mouseInput').OnMouseMove(uicore.uilib.dx, uicore.uilib.dy, self.entityID)



    def OnMouseEnter(self, *args):
        uicore.animations.FadeIn(self.hoverFill, endVal=0.4, duration=0.3)
        uicore.animations.BlinkIn(self.hoverLabel)



    def OnMouseExit(self, *args):
        uicore.animations.FadeOut(self.hoverFill)
        uicore.animations.FadeOut(self.hoverLabel)



    def GetMenu(self):
        m = sm.GetService('contextMenuClient').GetMenuForEntityID(self.entityID)
        if session.role & service.ROLE_QA:
            m += [('QA: Reload screen', sm.GetService('holoscreen').ReloadCorpFinderScreen)]
        return m




class PIScreen(uicls.Container):
    __guid__ = 'cqscreen.PIScreen'
    default_name = 'PIScreen'
    default_state = uiconst.UI_NORMAL
    default_opacity = 1.0
    default_align = uiconst.CENTER
    default_width = 540
    default_height = 720

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.entityID = attributes.entityID
        self.cursor = uiconst.UICURSOR_SELECT
        self.hoverFill = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.0), padding=-50)
        uicls.ScreenFrame1(parent=self, align=uiconst.TOALL, padding=10)
        self.circles = []
        for i in xrange(1, 5):
            transform = uicls.Transform(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=540, height=540, top=-26)
            circle = uicls.Sprite(parent=transform, texturePath='res:/UI/Texture/Classes/CQSideScreens/circle%s.png' % i, align=uiconst.TOALL)
            self.circles.append(transform)

        self.hoverLabel = uicls.Label(name='hoverLabel', parent=self, text=localization.GetByLabel('UI/Common/LocationTypes/Planets'), align=uiconst.CENTERBOTTOM, top=60, uppercase=True, fontsize=35, state=uiconst.UI_DISABLED, color=util.Color.WHITE)
        self.hoverLabel.opacity = 0.0
        self.bgSprite = uicls.Sprite(parent=self, texturePath='res:/UI/Texture/Classes/CQSideScreens/PIScreenBG.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=-50)
        uthread.new(self.AnimCircles)



    def OnClick(self, *args):
        sm.GetService('actionObjectClientSvc').TriggerDefaultActionOnObject(session.charid, self.entityID)



    def OnMouseEnter(self, *args):
        uicore.animations.FadeIn(self.hoverFill, endVal=0.4, duration=0.3)
        uicore.animations.BlinkIn(self.hoverLabel)



    def OnMouseExit(self, *args):
        uicore.animations.FadeOut(self.hoverFill)
        uicore.animations.FadeOut(self.hoverLabel)



    def OnMouseDown(self, button, *args):
        sm.GetService('mouseInput').OnMouseDown(button, uicore.uilib.x, uicore.uilib.y, self.entityID)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)



    def OnGlobalMouseUp(self, *args):
        if not uiutil.IsUnder(uicore.uilib.mouseOver, self):
            self.OnMouseExit()



    def OnMouseUp(self, button, *args):
        sm.GetService('mouseInput').OnMouseUp(button, uicore.uilib.x, uicore.uilib.y, self.entityID)



    def OnMouseMove(self, *args):
        sm.GetService('mouseInput').OnMouseMove(uicore.uilib.dx, uicore.uilib.dy, self.entityID)



    def GetMenu(self):
        m = sm.GetService('contextMenuClient').GetMenuForEntityID(self.entityID)
        if session.role & service.ROLE_QA:
            m += [('QA: Reload screen', sm.GetService('holoscreen').ReloadPIScreen)]
        return m



    def AnimCircles(self):
        speedFactor = [4,
         2,
         3,
         1]
        speedConst = 0.3
        while not self.destroyed:
            duration = random.randint(7, 15)
            for (i, circle,) in enumerate(self.circles):
                angleBase = speedConst * random.random() * random.choice([1, -1])
                uicore.animations.Tr2DRotateTo(circle, startAngle=circle.rotation, endAngle=circle.rotation + angleBase * speedFactor[i] * math.pi, duration=duration)

            blue.synchro.SleepWallclock(duration * 1000)
            uthread.new(self.AnimBackground)




    def AnimBackground(self):
        loops = random.randint(1, 4)
        uicore.animations.SpGlowFadeOut(self.bgSprite, loops=loops, duration=0.4 / loops)
        blue.synchro.SleepWallclock(random.randint(1000, 5000))




