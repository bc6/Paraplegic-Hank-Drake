import uicls
import uiconst
import blue
import bluepy
import util
import uiutil
import uthread
import random
import form
import trinity
import localization
import log
BG_GRAY = (0.15, 0.15, 0.15, 1.0)
TEMPLATE_DURATION = 12000

class BaseTemplate(uicls.Container):
    __guid__ = 'cqscreen.templates._Base'
    default_name = 'BaseTemplate'
    default_padLeft = 15
    default_padTop = 15
    default_padRight = 15
    default_padBottom = 15

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.uiDesktop = attributes.get('uiDesktop', None)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PlayIntro(self, videoPath):
        if not videoPath:
            return 
        video = uicls.VideoSprite(parent=self, videoPath=videoPath, align=uiconst.TOALL, padding=(-128, -132, -128, -132), positionComponent=getattr(self.uiDesktop, 'positionComponent', None))
        while not video.isFinished:
            blue.synchro.Yield()

        video.Close()
        uicore.animations.FadeIn(self, duration=0.3)




class SOV(BaseTemplate):
    __guid__ = 'cqscreen.templates.SOV'
    default_name = 'SovereigntyTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        leftFrame = uicls.ScreenFrame1(parent=self, align=uiconst.TOPLEFT, pos=(60, 50, 400, 400))
        uiutil.GetOwnerLogo(leftFrame.mainCont, data.oldOwnerID, size=400)
        blue.pyos.synchro.SleepWallclock(100)
        uicore.animations.FadeIn(leftFrame.mainCont, duration=0.1, loops=3)
        rightFrame = uicls.ScreenFrame1(parent=self, align=uiconst.TOPRIGHT, pos=(60, 50, 400, 400))
        uiutil.GetOwnerLogo(rightFrame.mainCont, data.newOwnerID, size=400)
        uicore.animations.FadeIn(rightFrame.mainCont, duration=0.1, loops=3)
        text = '<center>' + localization.GetByLabel('UI/Station/Holoscreen/SOV/SovereigntyChange') + '<center>'
        headingLabel = uicls.Label(parent=self, text=text, align=uiconst.CENTER, bold=True, color=util.Color.WHITE, fontsize=40, pos=(0, -120, 300, 0))
        uicore.animations.BlinkIn(headingLabel)
        text = '<center>' + data.middleText + '<center>'
        label = uicls.Label(parent=self, text=text, align=uiconst.CENTER, bold=True, fontsize=25, pos=(0, -20, 230, 0))
        uicore.animations.BlinkIn(label)
        banner = uicls.TextBanner(parent=self, align=uiconst.TOBOTTOM, padTop=10, scrollText=False, text=data.bottomText, fontSize=30, leftContWidth=310)
        uicls.Sprite(parent=banner.leftCont, pos=(30, -20, 252, 114), texturePath='res:/UI/Texture/Classes/CQMainScreen/scopeNewsLogo.png')
        uicore.animations.BlinkIn(banner)
        blue.pyos.synchro.SleepWallclock(TEMPLATE_DURATION)




class CareerAgent(BaseTemplate):
    __guid__ = 'cqscreen.templates.CareerAgent'
    default_name = 'CareerAgentTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        self.leftCont = uicls.Container(parent=self, align=uiconst.TOLEFT, width=640, padRight=10)
        self.rightCont = uicls.ScreenFrame5(parent=self, align=uiconst.TOALL)
        headingCont = uicls.Container(parent=self.leftCont, align=uiconst.TOTOP, height=100, bgColor=(0.35, 0.35, 0.35, 1.0))
        uicls.Label(parent=headingCont, text=data.headingText, fontsize=80, align=uiconst.CENTER, color=util.Color.WHITE, uppercase=True, bold=True)
        blue.pyos.synchro.SleepWallclock(300)
        uicls.ScreenHeading2(parent=self.leftCont, appear=True, align=uiconst.TOTOP, text=data.subHeadingText)
        frame = uicls.ScreenFrame4(parent=self.leftCont, align=uiconst.TOALL, appear=True, padTop=10)
        frame.mainCont.padLeft = 30
        frame.mainCont.padTop = 20
        uicls.Label(name='charNameLabel', parent=frame.mainCont, text=cfg.eveowners.Get(data.charID).name, fontsize=35, left=290)
        pictureCont = uicls.Container(align=uiconst.TOPLEFT, parent=frame.mainCont, pos=(0, 8, 256, 256))
        uicls.Frame(parent=pictureCont, color=util.Color.WHITE)
        uiutil.GetOwnerLogo(pictureCont, data.charID, size=256)
        uicls.EveLabelMedium(name='mainTextLabel', parent=frame.mainCont, pos=(290, 45, 300, 0), text=data.mainText)
        video = uicls.VideoSprite(parent=self.rightCont.mainCont, videoPath=data.careerVideoPath, align=uiconst.TOALL, repeat=True, positionComponent=getattr(self.uiDesktop, 'positionComponent', None))
        while not video.isFinished:
            blue.synchro.Yield()





class Incursion(BaseTemplate):
    __guid__ = 'cqscreen.templates.Incursion'
    default_name = 'IncursionTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        leftCont = uicls.Container(parent=self, align=uiconst.TOLEFT, width=845, padRight=10)
        rightCont = uicls.ScreenFrame5(parent=self, align=uiconst.TOALL)
        headingCont = uicls.Container(parent=leftCont, align=uiconst.TOTOP, height=100, fontsize=50)
        fill = uicls.Fill(bgParent=headingCont, color=(1.0, 0.0, 0.0, 0.5))
        uicore.animations.FadeTo(fill, startVal=0.5, endVal=0.2, duration=1.0, loops=uiconst.ANIM_REPEAT)
        label = uicls.Label(parent=headingCont, text=data.headingText, fontsize=80, align=uiconst.CENTER, color=util.Color.WHITE, uppercase=True, bold=True)
        frame = uicls.ScreenFrame1(parent=leftCont, align=uiconst.TOALL, appear=True, padTop=10)
        frame.mainCont.padTop = 70
        banner = uicls.TextBanner(parent=frame.mainCont, align=uiconst.TOBOTTOM, padTop=10, scrollText=False, text=data.bottomText, fontSize=30, leftContWidth=310)
        uicls.Sprite(parent=banner.leftCont, pos=(10, -20, 300, 100), texturePath='res:/UI/Texture/Classes/CQMainScreen/concordLogo.png')
        uicls.Label(parent=frame.mainCont, left=20, top=0, text=localization.GetByLabel('UI/Common/Constellation'), fontsize=30)
        uicls.Label(parent=frame.mainCont, left=20, top=30, text=data.constellationText, fontsize=45)
        uicls.Label(parent=frame.mainCont, left=280, top=0, text=localization.GetByLabel('UI/Incursion/Journal/StagingSystem'), fontsize=30)
        uicls.Label(parent=frame.mainCont, left=280, top=30, text=data.systemInfoText, fontsize=45)
        uicls.Label(parent=frame.mainCont, left=20, top=140, text=localization.GetByLabel('UI/Incursion/Common/HUDInfluenceTitle'), fontsize=30)
        influenceBar = uicls.SystemInfluenceBar(parent=frame.mainCont, align=uiconst.TOPLEFT, pos=(20, 180, 700, 60))
        influenceBar.SetInfluence(data.influence, True)
        uicore.animations.BlinkIn(frame.mainCont, sleep=True)
        video = uicls.VideoSprite(parent=rightCont.mainCont, videoPath=data.videoPath, align=uiconst.TOALL, repeat=True, positionComponent=getattr(self.uiDesktop, 'positionComponent', None))
        while not video.isFinished:
            blue.synchro.Yield()





class ShipExposure(BaseTemplate):
    __guid__ = 'cqscreen.templates.ShipExposure'
    default_name = 'ShipExposureTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        leftCont = uicls.Container(parent=self, align=uiconst.TOLEFT, width=500, padRight=10)
        topLeftCont = uicls.ScreenFrame4(parent=leftCont, align=uiconst.TOTOP, height=200)
        blue.pyos.synchro.SleepWallclock(600)
        uicore.animations.BlinkIn(topLeftCont.mainCont)
        topLeftCont.mainCont.padTop = 15
        topLeftCont.mainCont.padLeft = 20
        uicls.Label(parent=topLeftCont.mainCont, text=data.shipName, fontsize=60, align=uiconst.TOTOP)
        uicls.Label(parent=topLeftCont.mainCont, text=data.shipGroupName, fontsize=30, align=uiconst.TOTOP, padTop=-10)
        trainCont = uicls.Container(name='trainCont', parent=topLeftCont.mainCont, align=uiconst.BOTTOMLEFT, bgColor=(0, 0.3, 0, 1.0), pos=(0, 20, 270, 50))
        uicls.Label(parent=trainCont, text=data.buttonText, fontsize=20, align=uiconst.CENTER, bold=True)
        bottomFrame = uicls.ScreenFrame2(parent=leftCont, align=uiconst.TOALL, padTop=10)
        bottomFrame.mainCont.clipChildren = True
        bottomFrame.mainCont.padBottom = 5
        bottomFrame.mainCont.padTop = 15
        blue.pyos.synchro.SleepWallclock(300)
        label = uicls.EveLabelMedium(parent=bottomFrame.mainCont, text=data.mainText, width=480, align=uiconst.CENTERTOP, top=40)
        label.opacity = 0.0
        uicore.animations.BlinkIn(label, sleep=True)
        (w, h,) = bottomFrame.GetAbsoluteSize()
        if label.height + label.top > h:
            endVal = h - (label.height + label.top)
            endVal = min(-100, endVal)
            uicore.animations.MorphScalar(obj=label, attrName='top', startVal=label.top, endVal=endVal, duration=TEMPLATE_DURATION / 1000.0 + 1.0, curveType=uiconst.ANIM_LINEAR)
        rightFrame = uicls.ScreenFrame5(parent=self, align=uiconst.TOALL)
        fill = uicls.Fill(parent=rightFrame.mainCont, color=(0.5, 0.5, 0.5, 1.0))
        uicore.animations.FadeIn(fill, sleep=True)
        uicls.Scene3dCont(parent=rightFrame.mainCont, typeID=data.shipTypeID, opacity=0.0, duration=TEMPLATE_DURATION / 1000.0)
        blue.pyos.synchro.SleepWallclock(100)
        uicore.animations.BlinkOut(fill, sleep=True)
        blue.pyos.synchro.SleepWallclock(TEMPLATE_DURATION)




class RacialEpicArc(BaseTemplate):
    __guid__ = 'cqscreen.templates.RacialEpicArc'
    default_name = 'RacialEpicArcTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        uicls.TextBanner(parent=self, align=uiconst.TOBOTTOM, height=100, text=data.bottomText)
        rightCont = uicls.ScreenFrame5(parent=self, align=uiconst.TORIGHT, width=700, padLeft=10, padBottom=10)
        blue.pyos.synchro.SleepWallclock(300)
        topLeftCont = uicls.ScreenFrame2(parent=self, align=uiconst.TOTOP, height=300)
        bottomLeftCont = uicls.ScreenHeading1(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), padTop=10, padBottom=10, leftContWidth=150, appear=False)
        blue.pyos.synchro.SleepWallclock(300)
        uicls.ScreenHeading2(parent=topLeftCont.mainCont, text=localization.GetByLabel('UI/Station/Holoscreen/RacialEpicArc/EpicArcAgent'), align=uiconst.TOBOTTOM, hasBargraph=False, padBottom=10, padRight=10)
        topLeftCont.mainCont.padLeft = 30
        topLeftCont.mainCont.padTop = 15
        pictureCont = uicls.Container(align=uiconst.TOPLEFT, parent=topLeftCont.mainCont, pos=(0, 20, 180, 180))
        uicls.Frame(parent=pictureCont, color=util.Color.WHITE)
        uiutil.GetOwnerLogo(pictureCont, data.charID, size=256)
        logo = pictureCont.children[1]
        logo.align = uiconst.TOALL
        logo.width = logo.height = 0
        uicls.Label(name='charNameLabel', parent=topLeftCont.mainCont, text=cfg.eveowners.Get(data.charID).name, fontsize=50, left=200, top=20, color=util.Color.WHITE)
        uicls.EveLabelMedium(name='charLocationLabel', parent=topLeftCont.mainCont, pos=(200, 75, 300, 0), text=data.mainText)
        uicore.animations.BlinkIn(topLeftCont.mainCont)
        uiutil.GetOwnerLogo(bottomLeftCont.leftCont, data.factionID, size=150)
        icon = bottomLeftCont.leftCont.children[0]
        icon.align = uiconst.CENTER
        uicls.Label(parent=bottomLeftCont.mainCont, text=data.factionNameText, fontsize=42, top=30, left=15)
        uicls.Label(parent=bottomLeftCont.mainCont, text=localization.GetByLabel('UI/Agents/MissionTypes/EpicArc'), fontsize=30, top=80, left=15)
        bottomLeftCont.AnimAppear()
        video = uicls.VideoSprite(parent=rightCont.mainCont, videoPath=data.videoPath, align=uiconst.TOALL, positionComponent=getattr(self.uiDesktop, 'positionComponent', None))
        while not video.isFinished:
            blue.synchro.Yield()





class FullscreenVideo(BaseTemplate):
    __guid__ = 'cqscreen.templates.FullscreenVideo'
    default_name = 'FullscreenVideo'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        frame = uicls.ScreenFrame4(parent=self, align=uiconst.TOALL)
        blue.pyos.synchro.SleepWallclock(300)
        video = uicls.VideoSprite(parent=frame.mainCont, videoPath=data.videoPath, align=uiconst.TOALL, positionComponent=getattr(self.uiDesktop, 'positionComponent', None))
        uicore.animations.BlinkIn(frame.mainCont, loops=4)
        while not video.isFinished:
            blue.synchro.Yield()





class CharacterInfo(BaseTemplate):
    __guid__ = 'cqscreen.templates.CharacterInfo'
    default_name = 'CharacterInfoTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        banner = uicls.TextBanner(parent=self, align=uiconst.TOBOTTOM, padTop=10, scrollText=False, text=data.bottomText, fontSize=35, leftContWidth=310)
        uicls.Sprite(parent=banner.leftCont, pos=(10, -20, 300, 100), texturePath='res:/UI/Texture/Classes/CQMainScreen/concordLogo.png')
        uicore.animations.BlinkIn(banner, sleep=True)
        iconFrame = uicls.ScreenFrame5(parent=self, align=uiconst.TOPLEFT, pos=(100, 10, 450, 450), appear=True)
        blue.pyos.synchro.SleepWallclock(300)
        uiutil.GetOwnerLogo(iconFrame.mainCont, data.charID, size=512)
        icon = iconFrame.mainCont.children[0]
        icon.width = icon.height = 0
        icon.align = uiconst.TOALL
        if data.isWanted:
            wantedCont = uicls.Container(parent=iconFrame.mainCont, align=uiconst.BOTTOMLEFT, width=iconFrame.width, height=90, idx=0)
            fill = uicls.Fill(bgParent=wantedCont, color=(1.0, 0.0, 0.0, 0.5))
            uicore.animations.FadeTo(fill, startVal=0.5, endVal=0.2, duration=1.0, loops=uiconst.ANIM_REPEAT)
            label = uicls.Label(parent=wantedCont, text=data.wantedHeading, fontsize=50, align=uiconst.CENTERTOP, color=util.Color.WHITE, bold=True)
        uicore.animations.SpGlowFadeOut(icon, duration=0.1, loops=3, sleep=True)
        frame = uicls.ScreenFrame4(parent=self, align=uiconst.TOPRIGHT, pos=(100, 50, 500, 400), appear=True)
        blue.pyos.synchro.SleepWallclock(300)
        uicls.Fill(bgParent=frame.mainCont, color=BG_GRAY)
        uicls.Label(name='heading', parent=frame.mainCont, text=data.heading, fontsize=40, left=20, top=20, uppercase=True, bold=True)
        uicls.EveLabelMedium(name='mainTextLabel', parent=frame.mainCont, pos=(20, 70, 480, 0), text=data.mainText)
        uicore.animations.BlinkIn(frame.mainCont)
        if data.isWanted:
            label = uicls.Label(parent=frame.mainCont, text=data.wantedText, fontsize=45, top=-50, color=(0.6, 0.0, 0.0, 1.0), bold=True)
        blue.pyos.synchro.SleepWallclock(TEMPLATE_DURATION)




class Plex(BaseTemplate):
    __guid__ = 'cqscreen.templates.Plex'
    default_name = 'PlexTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        leftFrame = uicls.ScreenFrame5(parent=self, align=uiconst.TOLEFT, width=700)
        uicls.Sprite(name='plexLogo', parent=leftFrame.mainCont, align=uiconst.TOPLEFT, pos=(10, 30, 262, 326), texturePath='res:/UI/Texture/Classes/CQMainScreen/plexLogo.png')
        uicls.Label(name='heading', parent=leftFrame.mainCont, pos=(310, 20, 380, 0), text=data.headingText, fontsize=70, uppercase=True, bold=True)
        uicls.Label(name='subHeading', parent=leftFrame.mainCont, pos=(310, 85, 380, 0), text=data.subHeadingText, fontsize=35)
        greenCont = uicls.Container(name='trainCont', parent=leftFrame.mainCont, align=uiconst.TOPLEFT, bgColor=(0, 0.3, 0, 1.0), pos=(310, 143, 370, 50))
        uicls.Label(parent=greenCont, text=data.buttonText, fontsize=20, align=uiconst.CENTER, bold=True)
        uicls.Label(parent=leftFrame.mainCont, pos=(10, 250, 690, 0), text=data.mainText, fontsize=35)
        uicls.Sprite(parent=leftFrame.mainCont, align=uiconst.BOTTOMRIGHT, pos=(10, 30, 300, 100), texturePath='res:/UI/Texture/Classes/CQMainScreen/concordLogo.png')
        leftFrame.mainCont.opacity = 0.0
        blue.synchro.SleepWallclock(300)
        uicore.animations.BlinkIn(leftFrame.mainCont, sleep=True)
        rightFrame = uicls.ScreenFrame1(parent=self, align=uiconst.TORIGHT, width=540)
        blue.synchro.SleepWallclock(300)
        self.auraSprite = uicls.Sprite(name='aura', parent=rightFrame.mainCont, texturePath='res:/UI/Texture/Classes/CQMainScreen/aura.png', align=uiconst.CENTER, width=470, height=470)
        uthread.new(BlinkSprite, self.auraSprite)
        blue.pyos.synchro.SleepWallclock(TEMPLATE_DURATION)




class AuraMessage(BaseTemplate):
    __guid__ = 'cqscreen.templates.AuraMessage'
    default_name = 'AuraMessageTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        self.PlayIntro(data.get('introVideoPath', None))
        leftFrame = uicls.ScreenFrame5(parent=self, align=uiconst.TOPLEFT, pos=(80, 50, 450, 450))
        self.auraSprite = uicls.Sprite(name='aura', parent=leftFrame.mainCont, texturePath='res:/UI/Texture/Classes/CQMainScreen/aura.png', align=uiconst.TOALL)
        uthread.new(BlinkSprite, self.auraSprite)
        rightFrame = uicls.ScreenFrame2(parent=self, align=uiconst.TOPRIGHT, pos=(80, 50, 550, 300))
        blue.pyos.synchro.SleepWallclock(600)
        uicore.animations.BlinkIn(rightFrame.mainCont)
        rightFrame.mainCont.padTop = 30
        rightFrame.mainCont.padLeft = 30
        rightFrame.mainCont.padRight = 30
        lblHead = uicls.Label(parent=rightFrame.mainCont, text=data.headingText, fontsize=50, align=uiconst.TOTOP, uppercase=True, bold=True)
        lblBody = uicls.Label(parent=rightFrame.mainCont, text=data.subHeadingText, fontsize=35, align=uiconst.TOTOP, padTop=10)
        rightFrame.height = lblHead.height + lblBody.height + 65
        blue.pyos.synchro.SleepWallclock(TEMPLATE_DURATION)




class CloneStatus(BaseTemplate):
    __guid__ = 'cqscreen.templates.CloneStatus'
    default_name = 'CloneStatusTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        if data is None:
            return 
        top = uicls.Container(parent=self, align=uiconst.TOTOP, height=200)
        bottom = uicls.Container(parent=self)
        sf = uicls.ScreenFrame1(parent=top, align=uiconst.TOLEFT, width=200, padding=10, wedgeWidth=10)
        blue.pyos.synchro.SleepWallclock(30)
        sf = uicls.ScreenFrame2(parent=top, padding=10)
        blue.pyos.synchro.SleepWallclock(30)
        blue.pyos.synchro.SleepWallclock(3000)
        blue.pyos.synchro.SleepWallclock(TEMPLATE_DURATION)




class VirtualGoodsStore(BaseTemplate):
    __guid__ = 'cqscreen.templates.VirtualGoodsStore'
    default_name = 'VirtualGoodsStoreTemplate'

    @bluepy.CCP_STATS_ZONE_METHOD
    def Play(self, data):
        self.PlayIntro(data.get('introVideoPath', None))
        frame = uicls.ScreenFrame5(parent=self, align=uiconst.TOALL)
        uicls.Label(name='headingLabel', parent=frame.mainCont, align=uiconst.CENTERTOP, fontsize=80, text=data.headingText, uppercase=True, bold=True, top=30)
        uicore.animations.BlinkIn(frame.mainCont, sleep=True)
        blue.synchro.SleepWallclock(300)
        img1 = uicls.Sprite(name='img1', parent=frame.mainCont, pos=(10, 130, 380, 285), align=uiconst.TOPLEFT)
        uicore.animations.BlinkIn(img1, duration=0.05, sleep=True)
        img2 = uicls.Sprite(name='img2', parent=frame.mainCont, pos=(0, 130, 380, 285), align=uiconst.CENTERTOP)
        uicore.animations.BlinkIn(img2, duration=0.05, sleep=True)
        img3 = uicls.Sprite(name='img3', parent=frame.mainCont, pos=(10, 130, 380, 285), align=uiconst.TOPRIGHT)
        uicore.animations.BlinkIn(img3, duration=0.05, sleep=True)
        for (i, sprite,) in enumerate((img1, img2, img3)):
            imgPath = sm.GetService('photo').GetStorebanner(i + 1, prefs.languageID, sprite)
            if imgPath is None:
                sm.GetService('photo').GetStorebanner(i + 1, 'EN', sprite)

        blue.pyos.synchro.SleepWallclock(TEMPLATE_DURATION)




class Scene3dCont(uicls.Container):
    __guid__ = 'uicls.Scene3dCont'
    default_typeID = None

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.duration = attributes.duration
        self.sceneContainer = form.SceneContainer(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.sceneContainer.Startup()
        self.sceneContainer.PrepareSpaceScene()
        self.PreviewType(attributes.typeID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PreviewType(self, typeID, subsystems = None):
        typeOb = cfg.invtypes.Get(typeID)
        groupID = typeOb.groupID
        groupOb = cfg.invgroups.Get(groupID)
        categoryID = groupOb.categoryID
        godma = sm.GetService('godma')
        try:
            techLevel = godma.GetTypeAttribute(typeID, const.attributeTechLevel)
        except:
            techLevel = 1.0
        if categoryID == const.categoryShip and techLevel == 3.0:
            if subsystems is None:
                subsystems = {}
                subSystemsForType = {}
                for group in cfg.groupsByCategories.get(const.categorySubSystem, []):
                    if group.groupID not in subSystemsForType:
                        subSystemsForType[group.groupID] = []
                    for t in cfg.typesByGroups.get(group.groupID, []):
                        if t.published and godma.GetTypeAttribute(t.typeID, const.attributeFitsToShipType) == typeID:
                            subSystemsForType[group.groupID].append(t.typeID)


                for (k, v,) in subSystemsForType.iteritems():
                    subsystems[k] = random.choice(v)

            model = sm.StartService('t3ShipSvc').GetTech3ShipFromDict(typeID, subsystems)
        else:
            fileName = typeOb.GraphicFile()
            if fileName == '':
                log.LogWarn('type', typeID, 'has no graphicFile')
                return 
            fileName = fileName.replace(':/Model', ':/dx9/Model').replace('.blue', '.red')
            fileName = fileName.partition(' ')[0]
            model = trinity.Load(fileName)
            if model is None:
                self.sceneContainer.ClearScene()
                raise UserError('PreviewNoModel')
            if getattr(model, 'boosters', None) is not None:
                model.boosters = None
            if getattr(model, 'modelRotationCurve', None) is not None:
                model.modelRotationCurve = None
            if getattr(model, 'modelTranslationCurve', None) is not None:
                model.modelTranslationCurve = None
        if hasattr(model, 'ChainAnimationEx'):
            model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self._CreateRotationCurve(model)
        self.sceneContainer.AddToScene(model)
        camera = self.sceneContainer.camera
        rad = model.GetBoundingSphereRadius()
        minZoom = rad + camera.frontClip
        camera.translationFromParent.z = minZoom * 2
        self.sceneContainer.UpdateViewPort()



    def _CreateRotationCurve(self, model):
        model.rotationCurve = trinity.TriYPRSequencer()
        model.rotationCurve.YawCurve = yawCurve = trinity.TriScalarCurve()
        yawCurve.start = blue.os.GetWallclockTime()
        yawCurve.extrapolation = trinity.TRIEXT_CONSTANT
        yawCurve.AddKey(0.0, -70.0, 0, 0, trinity.TRIINT_HERMITE)
        yawCurve.AddKey(self.duration, 70.0, 0, 0, trinity.TRIINT_HERMITE)
        model.rotationCurve.PitchCurve = pitchCurve = trinity.TriScalarCurve()
        pitchCurve.start = blue.os.GetWallclockTime()
        pitchCurve.extrapolation = trinity.TRIEXT_CONSTANT
        pitchCurve.AddKey(0.0, -10.0, 0, 0, trinity.TRIINT_HERMITE)
        pitchCurve.AddKey(self.duration, 10.0, 0, 0, trinity.TRIINT_HERMITE)




def BlinkSprite(sprite):
    while not sprite.destroyed:
        num = random.randint(2, 4)
        uicore.animations.SpGlowFadeOut(sprite, duration=0.4 / num, loops=num)
        uicore.animations.SpColorMorphTo(sprite, startColor=(0.3, 0.3, 0.3, 1.0), endColor=util.Color.WHITE, duration=1.0)
        blue.pyos.synchro.SleepWallclock(random.randint(3000, 5000))




