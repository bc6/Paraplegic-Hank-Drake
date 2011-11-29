import uiconst
import uicls
import random
import uthread
import uiutil
import log
import localization
import util
import ccConst
import blue
import base
import service
FILL_SELECTION = 0.2
TEXT_NORMAL = 0.8
MINSIDESIZE = 280
MAXMENUSIZE = 380
LEFTSIZE = 200

class BaseCharacterCreationStep(uicls.Container):
    __guid__ = 'uicls.BaseCharacterCreationStep'
    __notifyevents__ = ['OnHideUI', 'OnShowUI']
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL
    racialHeader = {const.raceCaldari: 384,
     const.raceMinmatar: 128,
     const.raceAmarr: 256,
     const.raceGallente: 0}
    raceHeaderPath = 'res:/UI/Texture/CharacterCreation/RACE_Titletext.dds'
    raceFontColor = {const.raceCaldari: (0.93, 0.94, 0.99, 1.0),
     const.raceMinmatar: (0.99, 0.95, 0.95, 1.0),
     const.raceAmarr: (0.99, 0.95, 0.92, 1.0),
     const.raceGallente: (0.99, 0.99, 0.92, 1.0)}

    def UpdateLayout(self):
        self.UpdateSideContainerWidth()



    def ApplyAttributes(self, attributes):
        sm.RegisterNotify(self)
        uicls.Container.ApplyAttributes(self, attributes)
        self.charSvc = sm.GetService('character')
        self._cameraActive = False
        self._activeSculptZone = None
        self._didSculptMotion = False
        self._latestPickTime = None
        self.sr.uiContainer = uicls.Container(name='uiContainer', parent=self, align=uiconst.TOALL)
        self.sr.leftSide = uicls.Container(name='leftSide', parent=self.sr.uiContainer, align=uiconst.TOLEFT, pos=(0, 0, 0, 0))
        self.sr.rightSide = uicls.Container(name='rightSide', parent=self.sr.uiContainer, align=uiconst.TORIGHT, pos=(0, 0, 0, 0))
        self.UpdateSideContainerWidth()
        settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})



    def UpdateSideContainerWidth(self):
        mainCenterSize = min(uicore.desktop.width, uicore.desktop.height)
        sideSize = max(MINSIDESIZE, (uicore.desktop.width - mainCenterSize) / 2)
        self.sr.leftSide.width = LEFTSIZE
        self.sr.rightSide.width = sideSize



    def GetInfo(self):
        return uicore.layer.charactercreation.GetInfo()



    def ValidateStepComplete(self):
        return True



    def GetPickInfo(self, pos):
        layer = uicore.layer.charactercreation
        layer.StartEditMode(mode='makeup', skipPickSceneReset=True, useThread=0)
        pickedMakeup = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='hair', skipPickSceneReset=True, useThread=0)
        pickedHair = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='bodyselect', skipPickSceneReset=True, useThread=0)
        pickedBody = layer.PassMouseEventToSculpt('LeftDown', *pos)
        layer.StartEditMode(mode='sculpt', skipPickSceneReset=True, useThread=0)
        pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
        reset = layer.PassMouseEventToSculpt('LeftUp', *pos)
        return (pickedMakeup,
         pickedHair,
         pickedBody,
         pickedSculpt)



    def OnDblClick(self, *args):
        if self.stepID == ccConst.BLOODLINESTEP:
            pos = (uicore.uilib.x, uicore.uilib.y)
            layer = uicore.layer.charactercreation
            if getattr(layer, 'bloodlineSelector', None) is not None:
                picked = layer.PickObject(pos)
                (bloodlineID, genderID,) = uicore.layer.charactercreation.bloodlineSelector.GetBloodlineAndGender(picked)
                if bloodlineID is not None:
                    if genderID is not None:
                        layer.Approve()



    def OnMouseDown(self, btn, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP,
         ccConst.PORTRAITSTEP,
         ccConst.RACESTEP,
         ccConst.BLOODLINESTEP):
            return 
        self.storedMousePos = None
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        layer = uicore.layer.charactercreation
        if btn == uiconst.MOUSELEFT and self.stepID == ccConst.BLOODLINESTEP:
            layer = uicore.layer.charactercreation
            if getattr(layer, 'bloodlineSelector', None) is not None:
                picked = layer.PickObject(pos)
                (bloodlineID, genderID,) = uicore.layer.charactercreation.bloodlineSelector.GetBloodlineAndGender(picked)
                if bloodlineID is not None:
                    uthread.new(layer.SelectBloodline, bloodlineID)
                if genderID is not None:
                    uthread.new(layer.SelectGender, genderID)
        if btn == uiconst.MOUSERIGHT and self.stepID not in (ccConst.RACESTEP, ccConst.BLOODLINESTEP):
            self._cameraActive = True
            self._activeSculptZone = None
        elif btn == uiconst.MOUSELEFT and not self._cameraActive and self.charSvc.IsSculptingReady():
            self._didSculptMotion = False
            self._latestPickTime = blue.os.GetWallclockTime()
            if self.CanSculpt():
                layer.StartEditMode(callback=self.ChangeSculptingCursor)
                pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
                if pickedSculpt >= 0:
                    self.storedMousePos = (uicore.uilib.x, uicore.uilib.y)
                    self.cursor = uiconst.UICURSOR_NONE
                    self._cameraActive = False
                    self._activeSculptZone = pickedSculpt
                else:
                    self._cameraActive = True
                self._activeSculptZone = None
            elif self.stepID == ccConst.PORTRAITSTEP:
                info = self.GetInfo()
                self.charSvc.StartPosing(info.charID, callback=self.ChangeSculptingCursor)
                pickedSculpt = layer.PassMouseEventToSculpt('LeftDown', *pos)
                if pickedSculpt >= 0:
                    self._cameraActive = False
                    self._activeSculptZone = pickedSculpt
                else:
                    self._cameraActive = True
                self._activeSculptZone = None
            self._cameraActive = True
            self._activeSculptZone = None
        elif btn == uiconst.MOUSELEFT and self.stepID == ccConst.CUSTOMIZATIONSTEP and not layer.CanChangeBaseAppearance():
            self._cameraActive = True
        else:
            return 
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        uicore.uilib.SetCapture(self)



    def OnMouseUp(self, btn, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            return 
        if getattr(self, 'storedMousePos', None) is not None:
            uicore.uilib.SetCursorPos(*self.storedMousePos)
            self.storedMousePos = None
        if btn == uiconst.MOUSELEFT:
            uicore.layer.charactercreation.PassMouseEventToSculpt('LeftUp', uicore.uilib.x, uicore.uilib.y)
            if self.CanSculpt():
                if self._activeSculptZone is not None and self._didSculptMotion:
                    uicore.layer.charactercreation.TryStoreDna(False, 'Sculpting', sculpting=True)
                    charID = uicore.layer.charactercreation.GetInfo().charID
                    sm.ScatterEvent('OnDollUpdated', charID, False, 'sculpting')
                    self.charSvc.UpdateTattoos(charID)
                elif self._latestPickTime:
                    if blue.os.TimeDiffInMs(self._latestPickTime, blue.os.GetWallclockTime()) < 250.0:
                        (pickedMakeup, pickedHair, pickedBody, pickedSculpt,) = self.GetPickInfo((uicore.uilib.x, uicore.uilib.y))
                        log.LogInfo('Pickinfo: makeup, hair, bodyselect, sculpt = ', pickedMakeup, pickedHair, pickedBody, pickedSculpt)
                        for each in (('hair', pickedHair),
                         ('makeup', pickedMakeup),
                         ('clothes', pickedBody),
                         ('sculpt', pickedSculpt)):
                            if each in ccConst.PICKMAPPING:
                                pickedModifier = ccConst.PICKMAPPING[each]
                                self.ExpandMenuByModifier(pickedModifier)
                                break

            self._activeSculptZone = None
        if not uicore.uilib.rightbtn and not uicore.uilib.leftbtn:
            uicore.layer.charactercreation.PassMouseEventToSculpt('Motion', uicore.uilib.x, uicore.uilib.y)
            self._cameraActive = False
            self._activeSculptZone = None
            self.cursor = uiconst.UICURSOR_DEFAULT
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() is self:
                uicore.uilib.ReleaseCapture()



    def OnMouseMove(self, *args):
        if self.stepID not in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            return 
        pos = (int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling))
        if self._cameraActive:
            if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
                uicore.layer.charactercreation.camera.Dolly(uicore.uilib.dy)
            if uicore.uilib.leftbtn:
                uicore.layer.charactercreation.camera.AdjustYaw(uicore.uilib.dx)
                if not uicore.uilib.rightbtn:
                    uicore.layer.charactercreation.camera.AdjustPitch(uicore.uilib.dy)
            elif uicore.uilib.rightbtn:
                uicore.layer.charactercreation.camera.Pan(uicore.uilib.dx, uicore.uilib.dy)
        elif self._activeSculptZone is not None and self.stepID == ccConst.CUSTOMIZATIONSTEP:
            uicore.layer.charactercreation.CheckDnaLog('OnMouseMove')
            self._didSculptMotion = True
        uicore.layer.charactercreation.PassMouseEventToSculpt('Motion', *pos)



    def OnMouseWheel(self, *args):
        if not uicore.layer.charactercreation.camera:
            return 
        uicore.layer.charactercreation.camera.Dolly(-uicore.uilib.dz)



    def ChangeSculptingCursor(self, zone, isFront, isHead):
        if self.destroyed:
            return 
        if self.stepID == ccConst.CUSTOMIZATIONSTEP:
            if isFront:
                cursor = ccConst.ZONEMAP.get(zone, uiconst.UICURSOR_DEFAULT)
            else:
                cursor = ccConst.ZONEMAP_SIDE.get(zone, uiconst.UICURSOR_DEFAULT)
            self.cursor = cursor
        elif self.stepID == ccConst.PORTRAITSTEP:
            if isHead:
                cursor = ccConst.ZONEMAP_ANIM.get(zone, uiconst.UICURSOR_DEFAULT)
            else:
                cursor = ccConst.ZONEMAP_ANIMBODY.get(zone, uiconst.UICURSOR_DEFAULT)
            self.cursor = cursor
        lastZone = getattr(self, '_lastZone', None)
        if lastZone != zone:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_play'))
            self._lastZone = zone
            if self._lastZone == -1:
                sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_stop'))



    def ExpandMenuByModifier(self, modifier):
        if not self.sr.assetMenu:
            return 
        lastParentGroup = None
        allMenus = [ each for each in self.sr.assetMenu.sr.mainCont.children if isinstance(each, uicls.CharCreationAssetPicker) ]
        for menu in allMenus:
            if not menu.isSubmenu:
                lastParentGroup = menu
            if getattr(menu, 'modifier', None) == modifier:
                if lastParentGroup and not lastParentGroup.IsExpanded():
                    uthread.new(lastParentGroup.Expand)
                uthread.new(menu.Expand)




    def OnHideUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_HIDDEN



    def OnShowUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_PICKCHILDREN



    def CanSculpt(self, *args):
        return self.stepID == ccConst.CUSTOMIZATIONSTEP and uicore.layer.charactercreation.CanChangeBaseAppearance() and getattr(self, 'menuMode', None) != getattr(self, 'TATTOOMENU', None)



    def IsDollReady(self, *args):
        if uicore.layer.charactercreation.doll is None:
            return False
        return not uicore.layer.charactercreation.doll.busyUpdating




class RaceStep(BaseCharacterCreationStep):
    __guid__ = 'uicls.RaceStep'
    stepID = ccConst.RACESTEP
    racialMovies = {const.raceCaldari: 'res:/video/charactercreation/caldari.bik',
     const.raceMinmatar: 'res:/video/charactercreation/minmatar.bik',
     const.raceAmarr: 'res:/video/charactercreation/amarr.bik',
     const.raceGallente: 'res:/video/charactercreation/gallente.bik'}
    racialMusic = {const.raceCaldari: 'wise:/music_switch_race_caldari',
     const.raceMinmatar: 'wise:/music_switch_race_minmatar',
     const.raceAmarr: 'wise:/music_switch_race_amarr',
     const.raceGallente: 'wise:/music_switch_race_gallente',
     None: 'music_switch_race_norace'}

    def ApplyAttributes(self, attributes):
        self.raceInfo = {}
        self.bloodlineInfo = {}
        self.movieStateCheckRunning = 0
        self.padding = 6
        self.raceID = None
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        info = self.GetInfo()
        if uicore.desktop.width <= 1360:
            fontsize = 12
        else:
            fontsize = 14
        self.sr.raceInfoCont = uicls.Container(name='raceInfoCont', parent=self.sr.uiContainer, align=uiconst.CENTERTOP, width=600, height=uicore.desktop.height, state=uiconst.UI_PICKCHILDREN)
        self.sr.textCont = uicls.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 38, 0, 20), state=uiconst.UI_NORMAL)
        header = uicls.CCLabel(text=localization.GetByLabel('UI/CharacterCreation/RaceSelection'), name='header', parent=self.sr.textCont, align=uiconst.CENTERTOP, uppercase=1, letterspace=2, color=(0.9, 0.9, 0.9, 0.8), fontsize=22, bold=False)
        self.sr.raceCont = uicls.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 40, 0, 80), state=uiconst.UI_NORMAL)
        self.raceSprite = uicls.Sprite(name='raceSprite', parent=self.sr.raceCont, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, texturePath=self.raceHeaderPath, pos=(0, 0, 512, 128))
        uicls.Container(name='push', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 0, 0, 15), state=uiconst.UI_DISABLED)
        self.sr.movieCont = uicls.Container(name='movieCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 0, 0, 338), state=uiconst.UI_HIDDEN)
        self.sr.raceTextCont = uicls.Container(name='raceTextCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, padding=(0,
         15,
         0,
         self.padding), state=uiconst.UI_HIDDEN)
        self.sr.raceText = uicls.CCLabel(parent=self.sr.raceTextCont, fontsize=fontsize, align=uiconst.TOPLEFT, text='', letterspace=0, top=0, pos=(0, 0, 600, 0), bold=0, color=ccConst.COLOR75)
        self.sr.buttonCont = uicls.Container(parent=self.sr.uiContainer, align=uiconst.CENTERBOTTOM, pos=(0, 60, 512, 128))
        for race in sm.GetService('cc').GetRaceData():
            raceBtn = uicls.RaceButton(name='raceBtn', parent=self.sr.buttonCont, align=uiconst.TOLEFT, pos=(0, 0, 128, 128), raceID=race.raceID)
            btnName = 'raceBtn_%s' % race.raceID
            setattr(self.sr, btnName, raceBtn)
            if info.raceID and info.raceID == race.raceID:
                raceBtn.Select()

        if info.raceID:
            self.raceID = info.raceID
            self.UpdateRaceHeader(info.raceID)
            self.GetRaceText()
        uicls.Frame(parent=self.sr.movieCont, color=(1.0, 1.0, 1.0, 0.2))
        self.sr.racialImage = uicls.Sprite(name='racialImage', parent=self.sr.movieCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.sr.movieCont.OnMouseEnter = self.OnMovieEnter
        self.movie = uicls.VideoSprite(parent=self.sr.movieCont, pos=(0, 0, 600, 338), videoPath=self.racialMovies.get(info.raceID, ''), videoAutoPlay=False)
        self.movie.display = False
        self.sr.movieControlCont = uicls.Container(name='controlCont', parent=self.sr.movieCont, align=uiconst.CENTERBOTTOM, pos=(0, 0, 60, 22), idx=0, state=uiconst.UI_HIDDEN)
        uicls.Fill(parent=self.sr.movieControlCont, padding=(0, 0, 0, 1), color=(0, 0, 0, 0.3))
        self.UpdateLayout()
        buttons = [('playpPauseBtn',
          4,
          'ui_73_16_225',
          self.ClickPlayPause), ('soundBtn',
          40,
          'ui_73_16_230',
          self.ClickSound), ('noSoundBtn',
          40,
          'ui_38_16_111',
          self.ClickSound)]
        for (name, left, iconPath, function,) in buttons:
            icon = uicls.Icon(parent=self.sr.movieControlCont, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, pos=(left,
             2,
             16,
             16), icon=iconPath, idx=0)
            icon.OnClick = function
            icon.OnMouseEnter = (self.MouseOverButton, icon)
            icon.OnMouseExit = (self.MouseExitButton, icon)
            icon.SetAlpha(0.5)
            self.sr.Set(name, icon)

        self.sr.noSoundBtn.state = uiconst.UI_HIDDEN
        self.setupDone = 1
        self.TryPlayMovie()



    def UpdateLayout(self):
        if not self.sr.raceInfoCont:
            return 
        if uicore.desktop.height <= 900:
            self.sr.raceInfoCont.width = 400
            self.sr.movieCont.height = 225
            self.sr.raceText.width = self.sr.raceInfoCont.width - self.padding * 2
            self.sr.raceText.fontsize = 12
            self.sr.buttonCont.top = 60
            self.sr.raceCont.top = 40
        else:
            self.sr.raceInfoCont.width = 600
            self.sr.raceText.width = self.sr.raceInfoCont.width - self.padding * 2
            self.sr.movieCont.height = 338
            self.sr.raceText.fontsize = 14
            self.sr.raceText.linespace = 16
            self.sr.buttonCont.top = 80
            self.sr.raceCont.top = 80
        uthread.new(self.UpdateTextHeight)
        self.movie.width = self.sr.raceInfoCont.width
        self.movie.height = self.sr.movieCont.height



    def UpdateTextHeight(self):
        blue.pyos.synchro.Yield()
        self.sr.raceTextCont.height = self.sr.raceText.textheight



    def OnRaceSelected(self, raceID, *args):
        for i in [const.raceAmarr,
         const.raceMinmatar,
         const.raceGallente,
         const.raceCaldari]:
            raceBtn = self.sr.Get('raceBtn_%d' % i)
            raceBtn.Deselect()

        btn = self.sr.Get('raceBtn_%d' % raceID)
        btn.Select()
        uicore.layer.charactercreation.UpdateBackdropLite(raceID)
        self.UpdateRaceHeader(raceID)
        self.UpdateRaceInfo(raceID)



    def UpdateRaceHeader(self, raceID):
        self.raceSprite.state = uiconst.UI_DISABLED
        height = 128
        top = self.racialHeader.get(raceID, None)
        (self.raceSprite.rectTop, self.raceSprite.rectHeight,) = (top, height)



    def UpdateRaceInfo(self, raceID):
        oldRaceID = self.raceID
        self.raceID = raceID
        racialMusic = self.racialMusic.get(raceID, None)
        uicore.layer.charactercreation.UpdateRaceMusic(raceID)
        sm.StartService('audio').SendUIEvent(unicode(racialMusic))
        if not uicore.layer.charactercreation.raceMusicStarted:
            bgMusic = sm.StartService('jukebox').GetState()
            if bgMusic == 'play':
                sm.StartService('jukebox').Pause()
            sm.StartService('audio').SendUIEvent(unicode('wise:/music_character_creation_play'))
            uicore.layer.charactercreation.raceMusicStarted = True
        self.TryPlayMovie(oldRaceID)
        self.GetRaceText()



    def GetRaceText(self):
        info = self.GetInfo()
        if info.raceID is None:
            return 
        if not len(self.raceInfo):
            self.raceInfo = sm.GetService('cc').GetRaceDataByID()
        self.sr.raceTextCont.state = uiconst.UI_NORMAL
        raceInfo = self.raceInfo[info.raceID]
        raceText = localization.GetByMessageID(raceInfo.descriptionID)
        color = self.raceFontColor.get(info.raceID, (1.0, 1.0, 1.0, 0.75))
        self.sr.raceText.text = raceText
        self.sr.raceText.color.SetRGB(*color)
        uthread.new(self.UpdateTextHeight)



    def TryPlayMovie(self, oldRaceID = None, *args):
        info = self.GetInfo()
        if info.raceID is None:
            return 
        self.sr.movieCont.state = uiconst.UI_NORMAL
        if not getattr(self, 'setupDone', 0):
            return 
        if info.raceID != oldRaceID:
            self.Pause()
            self.movie.SetVideoPath(self.racialMovies.get(info.raceID, None))
        if settings.user.ui.Get('cc_racialMoviePlayed_%s' % info.raceID, 0):
            self.ShowMovieRacialImage()
        else:
            uthread.new(self.MovieState)
            self.PlayMovie()



    def OnMovieEnter(self, *args):
        self.sr.movieControlCont.state = uiconst.UI_NORMAL



    def OnMouseEnter(self, *args):
        if self.sr.movieControlCont:
            self.sr.movieControlCont.state = uiconst.UI_HIDDEN



    def PlayMovie(self):
        info = self.GetInfo()
        if info.raceID is None:
            return 
        sm.StartService('audio').SendUIEvent(unicode('wise:/music_character_creation_stop'))
        uicore.layer.charactercreation.raceMusicStarted = False
        uthread.new(self.MovieState)
        self.movie.display = True
        self.movie.Play()
        settings.user.ui.Set('cc_racialMoviePlayed_%s' % info.raceID, 1)
        self.sr.racialImage.state = uiconst.UI_HIDDEN
        self.movie.state = uiconst.UI_DISABLED
        self.sr.playpPauseBtn.LoadIcon('ui_73_16_226')



    def ClickPlayPause(self, *args):
        if getattr(self, 'movie', None) is not None:
            if not getattr(self.movie, 'isPaused', None):
                self.Pause()
            else:
                self.PlayMovie()



    def Pause(self, *args):
        if not uicore.layer.charactercreation.raceMusicStarted:
            sm.StartService('audio').SendUIEvent(unicode('wise:/music_character_creation_play'))
        self.movie.Pause()
        self.sr.playpPauseBtn.LoadIcon('ui_73_16_225')



    def ClickSound(self, *args):
        if self.movie.isMuted:
            self.movie.UnmuteAudio()
            self.sr.noSoundBtn.state = uiconst.UI_HIDDEN
        else:
            self.movie.MuteAudio()
            self.sr.noSoundBtn.state = uiconst.UI_NORMAL



    def MouseOverButton(self, btn, *args):
        btn.SetAlpha(1.0)



    def MouseExitButton(self, btn, *args):
        btn.SetAlpha(0.5)



    def MovieState(self):
        if self.movieStateCheckRunning:
            return 
        self.movieStateCheckRunning = 1
        while self and not self.dead and self.movieStateCheckRunning:
            if getattr(self, 'movie', None) and self.sr:
                if getattr(self.movie, 'isPaused', None):
                    self.sr.playpPauseBtn.LoadIcon('ui_73_16_225')
                else:
                    self.sr.playpPauseBtn.LoadIcon('ui_73_16_226')
                if self.movie.isFinished:
                    self.ShowMovieRacialImage()
            blue.pyos.synchro.SleepWallclock(1000)

        if self and not self.dead:
            self.movieStateCheckRunning = 0



    def ShowMovieRacialImage(self, *args):
        info = self.GetInfo()
        if info.raceID not in [const.raceCaldari,
         const.raceMinmatar,
         const.raceAmarr,
         const.raceGallente]:
            return 
        self.movieStateCheckRunning = 0
        self.movie.display = False
        self.sr.racialImage.state = uiconst.UI_DISABLED
        self.sr.racialImage.LoadTexture('res:/UI/Texture/Charsel/movieImage_%s.dds' % info.raceID)
        if not uicore.layer.charactercreation.raceMusicStarted:
            sm.StartService('audio').SendUIEvent(unicode('wise:/music_character_creation_play'))




class CharacterBloodlineSelection(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterBloodlineSelection'
    stepID = ccConst.BLOODLINESTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.bloodlineInfo = {}
        self.bloodlineIDs = []
        info = self.GetInfo()
        self.raceID = info.raceID
        self.bloodlineID = info.bloodlineID
        self.isFemaleLeft = False
        self.sr.rightSide.width = self.sr.leftSide.width
        bloodlines = sm.GetService('cc').GetBloodlineDataByRaceID().get(self.raceID, [])[:]
        for bloodline in bloodlines:
            self.bloodlineIDs.append(bloodline.bloodlineID)

        self.sr.raceInfoCont = uicls.Container(name='raceInfoCont', parent=self.sr.uiContainer, align=uiconst.CENTERTOP, width=600, height=uicore.desktop.height, state=uiconst.UI_PICKCHILDREN)
        self.sr.textCont = uicls.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0, 38, 0, 20), state=uiconst.UI_DISABLED)
        self.sr.header = uicls.CCLabel(text=localization.GetByLabel('UI/CharacterCreation/BloodlineSelection'), name='header', parent=self.sr.textCont, align=uiconst.CENTERTOP, uppercase=1, letterspace=2, color=(0.9, 0.9, 0.9, 0.8), fontsize=22, bold=False)
        if uicore.desktop.height <= 900:
            top = 20
        else:
            top = 40
        self.sr.raceCont = uicls.Container(name='raceCont', parent=self.sr.raceInfoCont, align=uiconst.TOTOP, pos=(0,
         top,
         0,
         80), state=uiconst.UI_DISABLED)
        self.raceSprite = uicls.Sprite(name='raceSprite', parent=self.sr.raceCont, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, texturePath=self.raceHeaderPath, pos=(0, 0, 512, 128))
        self.raceSprite.state = uiconst.UI_DISABLED
        height = 128
        top = self.racialHeader.get(self.raceID, None)
        (self.raceSprite.rectTop, self.raceSprite.rectHeight,) = (top, height)
        for bloodlineID in self.bloodlineIDs:
            cont = uicls.Container(name='cont', parent=self.sr.uiContainer, align=uiconst.TOPLEFT, pos=(0, 0, 200, 128), state=uiconst.UI_HIDDEN)
            contName = 'cont_%d' % bloodlineID
            setattr(self.sr, contName, cont)
            contGender = uicls.Container(name='contGender', parent=cont, align=uiconst.CENTERBOTTOM, pos=(0, 4, 200, 64))
            contGenderName = 'contGender_%d' % bloodlineID
            setattr(self.sr, contGenderName, contGender)
            genderBtnFemale = uicls.GenderButton(name='GenderButton', parent=contGender, align=uiconst.BOTTOMLEFT, pos=(0, 0, 64, 64), genderID=0, raceID=self.raceID, state=uiconst.UI_HIDDEN)
            btnName = 'genderBtn_%d_%d' % (bloodlineID, 0)
            setattr(self.sr, btnName, genderBtnFemale)
            genderBtnMale = uicls.GenderButton(name='GenderButton', parent=contGender, align=uiconst.BOTTOMRIGHT, pos=(0, 0, 64, 64), genderID=1, raceID=self.raceID, state=uiconst.UI_HIDDEN)
            btnName = 'genderBtn_%d_%d' % (bloodlineID, 1)
            setattr(self.sr, btnName, genderBtnMale)
            btn = uicls.BloodlineButton(name='BloodlineButton', parent=cont, align=uiconst.CENTER, pos=(0, 0, 128, 128), bloodlineID=bloodlineID)
            btnName = 'bloodlineBtn_%d' % bloodlineID
            setattr(self.sr, btnName, btn)
            if info.bloodlineID and info.bloodlineID == bloodlineID:
                btn.Select()
                genderBtnFemale.state = uiconst.UI_NORMAL
                genderBtnMale.state = uiconst.UI_NORMAL
                if info.genderID is not None:
                    canChangeGender = uicore.layer.charactercreation.CanChangeGender()
                    if info.genderID == ccConst.GENDERID_FEMALE:
                        genderBtnFemale.Select()
                        if not canChangeGender:
                            genderBtnMale.state = uiconst.UI_HIDDEN
                    else:
                        genderBtnMale.Select()
                        if not canChangeGender:
                            genderBtnFemale.state = uiconst.UI_HIDDEN

        self.sr.bloodlineTextCont = uicls.Container(name='bloodlineTextCont', parent=self.sr.uiContainer, align=uiconst.TOBOTTOM, height=80, top=64, state=uiconst.UI_NORMAL)
        self.sr.bloodlineText = uicls.CCLabel(parent=self.sr.bloodlineTextCont, fontsize=12, align=uiconst.BOTTOMLEFT, width=600, text='', letterspace=0, top=0, bold=0)
        if info.bloodlineID:
            self.GetBloodlineText()



    def UpdateLayout(self):
        if uicore.desktop.height <= 900:
            self.sr.raceCont.top = 20
        else:
            self.sr.raceCont.top = 40
        self.MakeUI()
        uthread.new(self.GetTextWidth)



    def GetTextWidth(self):
        blue.pyos.synchro.Yield()
        (left, top, width, height,) = self.sr.bloodlineTextCont.GetAbsolute()
        self.sr.bloodlineText.width = width



    def OnBloodlineSelected(self, bloodlineID, *args):
        info = uicore.layer.charactercreation.GetInfo()
        if uicore.layer.charactercreation.CanChangeGender():
            uicore.layer.charactercreation.genderID = None
        self.sr.header.text = localization.GetByLabel('UI/CharacterCreation/GenderSelection')
        self.bloodlineID = bloodlineID
        for i in self.bloodlineIDs:
            bloodlineBtn = self.sr.Get('bloodlineBtn_%d' % i)
            bloodlineBtn.Deselect()
            genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (i, 0))
            genderBtnFemale.state = uiconst.UI_HIDDEN
            genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (i, 1))
            genderBtnMale.state = uiconst.UI_HIDDEN
            btnContainer = self.sr.Get('contGender_%d' % i)
            btnContainer.width = 140

        btn = self.sr.Get('bloodlineBtn_%d' % bloodlineID)
        btn.Select()
        btnContainer = self.sr.Get('contGender_%d' % bloodlineID)
        uicore.effect.MorphUI(btnContainer, 'width', 200, 350.0, ifWidthConstrain=0)
        if not uicore.layer.charactercreation.CanChangeGender() and info.genderID:
            genderBtn = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, info.genderID))
            genderBtn.state = uiconst.UI_NORMAL
            genderBtn.Select()
        else:
            genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 0))
            genderBtnFemale.state = uiconst.UI_NORMAL
            genderBtnFemale.Deselect()
            genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 1))
            genderBtnMale.state = uiconst.UI_NORMAL
            genderBtnMale.Deselect()
        self.GetBloodlineText()



    def OnGenderSelected(self, genderID, *args):
        genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (self.bloodlineID, 0))
        genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (self.bloodlineID, 1))
        if genderID == 0:
            genderBtnFemale.Select()
            genderBtnMale.Deselect()
        else:
            genderBtnFemale.Deselect()
            genderBtnMale.Select()



    def GetBloodlineText(self):
        info = self.GetInfo()
        if info.bloodlineID is None:
            return 
        if not len(self.bloodlineInfo):
            self.bloodlineInfo = sm.GetService('cc').GetBloodlineDataByID()
        color = self.raceFontColor.get(info.raceID, (1.0, 1.0, 1.0, 0.75))
        blinfo = self.bloodlineInfo[info.bloodlineID]
        bloodlineText = localization.GetByMessageID(blinfo.descriptionID)
        self.sr.bloodlineText.color.SetRGB(*color)
        self.sr.bloodlineText.text = bloodlineText
        uthread.new(self.GetTextWidth)



    def MakeUI(self):
        for bloodlineID in self.bloodlineIDs:
            uthread.new(self.GetBloodlinePos, bloodlineID)




    def GetBloodlinePos(self, bloodlineID):
        blue.resMan.Wait()
        camera = uicore.layer.charactercreation.camera
        left = top = 0
        if getattr(uicore.layer.charactercreation, 'bloodlineSelector', None) is not None:
            pos = uicore.layer.charactercreation.bloodlineSelector.GetProjectedPosition(bloodlineID, None, camera)
            self.isFemaleLeft = uicore.layer.charactercreation.bloodlineSelector.GetGenderOrder(bloodlineID)
        else:
            log.LogError('Trying to place bloodline UI, but bloodlineSelector is None!')
            pos = (0.0, 0.0)
        if pos:
            left = int(pos[0] / uicore.desktop.dpiScaling)
            top = int(pos[1] / uicore.desktop.dpiScaling)
        cont = self.sr.Get('cont_%d' % bloodlineID)
        cont.left = left - cont.width / 2
        cont.top = top - cont.height / 2 - 20
        cont.state = uiconst.UI_PICKCHILDREN
        if not self.isFemaleLeft:
            cont = self.sr.Get('cont_%d' % bloodlineID)
            genderBtnFemale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 0))
            genderBtnMale = self.sr.Get('genderBtn_%d_%d' % (bloodlineID, 1))
            genderBtnMale.SetAlign(uiconst.BOTTOMLEFT)
            genderBtnFemale.SetAlign(uiconst.BOTTOMRIGHT)




class CharacterCustomization(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterCustomization'
    __notifyevents__ = ['OnColorPaletteChanged', 'OnHideUI', 'OnShowUI']
    stepID = ccConst.CUSTOMIZATIONSTEP
    ASSETMENU = 1
    TATTOOMENU = 2

    def ApplyAttributes(self, attributes):
        uicore.event.RegisterForTriuiEvents(uiconst.UI_ACTIVE, self.CheckAppFocus)
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        info = self.GetInfo()
        self.menuMode = self.ASSETMENU
        self.charID = attributes.charID
        self.colorPaletteWidth = uicls.CCColorPalette.COLORPALETTEWIDTH
        self.tattooChangeMade = 0
        self.menusInitialized = 0
        self.sr.leftSide.width = 200
        self.sr.headBodyPicker = uicls.CCHeadBodyPicker(name='headBodyPicker', parent=self.sr.leftSide, align=uiconst.CENTERTOP, top=98, headCallback=self.LoadFaceMode, bodyCallback=self.LoadBodyMode)
        clickable = uicore.layer.charactercreation.CanChangeBloodline()
        if clickable and not uicore.layer.charactercreation.CanChangeGender():
            disabledHex = ['gender']
        else:
            disabledHex = []
        picker = uicls.CCRacePicker(parent=self.sr.uiContainer, align=uiconst.BOTTOMLEFT, raceID=info.raceID, bloodlineID=info.bloodlineID, genderID=info.genderID, padding=(30, 0, 0, -8), clickable=clickable, disabledHex=disabledHex)
        self.sr.assetMenuPar = uicls.Container(parent=self.sr.rightSide, name='assetMenuPar', pos=(0,
         0,
         MAXMENUSIZE,
         uicore.desktop.height), state=uiconst.UI_PICKCHILDREN, align=uiconst.CENTERTOP)
        self.sr.hintBox = uicls.Container(parent=self.sr.assetMenuPar, pos=(0, 20, 200, 150), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
        self.sr.hintText = uicls.EveLabelMedium(text='', parent=self.sr.hintBox, align=uiconst.TOTOP)
        self.sr.randomButton = uicls.Transform(parent=self.sr.headBodyPicker, pos=(-52, 34, 22, 22), state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, hint=localization.GetByLabel('UI/CharacterCreation/RandomizeAll'), idx=0)
        self.sr.randomButton.OnClick = self.RandomizeCharacter
        self.sr.randomButton.OnMouseEnter = (self.OnGenericMouseEnter, self.sr.randomButton)
        self.sr.randomButton.OnMouseExit = (self.OnGenericMouseExit, self.sr.randomButton)
        randIcon = uicls.Icon(parent=self.sr.randomButton, icon=ccConst.ICON_RANDOM, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
        self.sr.randomButton.sr.icon = randIcon
        self.sr.toggleClothesButton = uicls.Container(parent=self.sr.headBodyPicker, pos=(52, 32, 26, 26), state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, hint=localization.GetByLabel('UI/CharacterCreation/ToggleClothes'), idx=0)
        toggleIcon = uicls.Icon(parent=self.sr.toggleClothesButton, icon=ccConst.ICON_TOGGLECLOTHES, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
        self.sr.toggleClothesButton.OnClick = self.ToggleClothes
        self.sr.toggleClothesButton.OnMouseEnter = (self.OnGenericMouseEnter, self.sr.toggleClothesButton)
        self.sr.toggleClothesButton.OnMouseExit = (self.OnGenericMouseExit, self.sr.toggleClothesButton)
        self.sr.toggleClothesButton.sr.icon = toggleIcon
        self.UpdateLayout()
        self.StartLoadingThread()



    def StartLoadingThread(self, *args):
        if self.sr.loadingWheelThread:
            self.sr.loadingWheelThread.kill()
            self.sr.loadingWheelThread = None
        self.sr.loadingWheelThread = uthread.new(self.ShowLoadingWheel_thread)



    def SetHintText(self, modifier, hintText = ''):
        text = hintText
        if modifier in ccConst.HELPTEXTS:
            labelPath = ccConst.HELPTEXTS[modifier]
            text = localization.GetByLabel(labelPath)
        elif modifier == ccConst.eyes:
            labelPath = ccConst.HELPTEXTS[ccConst.EYESGROUP]
            text = localization.GetByLabel(labelPath)
        if text != self.sr.hintText.text:
            self.sr.hintText.text = text



    def ToggleClothes(self, *args):
        if uicore.layer.charactercreation.doll.busyUpdating:
            raise UserError('uiwarning01')
        uicore.layer.charactercreation.ToggleClothes()



    def OnGenderSelected(self, genderID):
        self.GoToAssetMode(animate=0, forcedMode=1)
        if self.sr.tattooMenu:
            self.sr.tattooMenu.Close()



    def UpdateLayout(self, *args):
        BaseCharacterCreationStep.UpdateLayout(self)
        self.colorPaletteWidth = uicls.CCColorPalette.COLORPALETTEWIDTH
        self.sr.assetMenuPar.height = uicore.desktop.height
        for menu in (self.sr.tattooMenu, self.sr.assetMenu):
            if menu and not menu.destroyed:
                menu.ChangeHeight(self.sr.assetMenuPar.height)

        self.sr.rightSide.width += self.colorPaletteWidth
        sm.GetService('cc').LogInfo('CharacterCustomization::UpdateLayout')
        if not self.menusInitialized:
            self.sr.tattooMenu = self.ReloadTattooMenu()
            self.sr.assetMenu = self.ReloadAssetMenu()
            self.menusInitialized = 1
        self.LoadMenu()



    def OnColorPaletteChanged(self, width, *args):
        if width > self.colorPaletteWidth:
            difference = width - self.colorPaletteWidth
            self.colorPaletteWidth = width
            self.sr.rightSide.width += difference
            self.sr.assetMenu.width += difference
            self.sr.assetMenuPar.width += difference
            self.sr.hintBox.left = self.assetMenuMainWidth + 20



    def RandomizeCharacter(self, randomizingPart = None, *args):
        info = self.GetInfo()
        doll = self.charSvc.GetSingleCharactersDoll(info.charID)
        if doll.busyUpdating:
            return 
        uicore.layer.charactercreation.LockNavigation()
        uicore.layer.charactercreation.ToggleClothes(forcedValue=0)
        uthread.new(self.RandomizeRotation_thread, self.sr.randomButton)
        itemList = []
        if info.genderID == ccConst.GENDERID_FEMALE:
            itemList = ccConst.femaleRandomizeItems.keys()
        else:
            itemList = ccConst.maleRandomizeItems.keys()
        canChangeBaseAppearance = uicore.layer.charactercreation.CanChangeBaseAppearance()
        blacklist = ccConst.randomizerCategoryBlacklist[:]
        if not canChangeBaseAppearance:
            blacklist += ccConst.recustomizationRandomizerBlacklist
        if info.genderID == ccConst.GENDERID_FEMALE:
            blacklist.append(ccConst.scarring)
        categoryList = []
        for item in itemList:
            if item not in blacklist:
                categoryList.append(item)

        self.charSvc.RandomizeCharacterGroups(info.charID, categoryList, doUpdate=False, fullRandomization=True)
        if canChangeBaseAppearance:
            self.charSvc.RandomizeCharacterSculpting(info.charID, doUpdate=False)
        decalModifiers = doll.buildDataManager.GetModifiersByCategory(ccConst.tattoo)
        for modifier in decalModifiers:
            modifier.IsDirty = True

        self.charSvc.UpdateDoll(info.charID, 'RandomizeCharacter')



    def RandomizeRotation_thread(self, randomButton, *args):
        randomButton.StartRotationCycle(cycleTime=750.0, cycles=5)
        if randomButton and not randomButton.dead:
            randomButton.SetRotation(0)



    def LoadMenu(self, animate = 0, forcedMode = 0, *arg):
        sm.GetService('cc').LogInfo('CharacterCustomization::LoadMenu')
        menu = None
        if self.menuMode == self.ASSETMENU:
            menu = self.GetAssetMenu(forcedMode)
        elif self.menuMode == self.TATTOOMENU:
            menu = self.GetTattooMenu(forcedMode)
        if menu is None:
            return 
        if animate:
            mainCont = menu.sr.mainCont
            if self.menuMode == self.TATTOOMENU:
                fullHeight = menu.sr.mainCont.height
                mainCont.height = menu.sr.menuToggler.height
                menu.state = uiconst.UI_DISABLED
                uicore.effect.MorphUIMassSpringDamper(mainCont, 'height', fullHeight, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
                menu.state = uiconst.UI_PICKCHILDREN
            else:
                menu.state = uiconst.UI_DISABLED
                uicore.effect.MorphUIMassSpringDamper(mainCont, 'top', 0, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
            menu.sr.mainCont.height = uicore.desktop.height
            menu.state = uiconst.UI_PICKCHILDREN
        else:
            menu.state = uiconst.UI_PICKCHILDREN
        menu.CheckIfOversize()



    def GetTattooMenu(self, forcedMode = 0, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::GetTattooMenu')
        if not forcedMode and self.sr.tattooMenu and not self.sr.tattooMenu.destroyed:
            if self.sr.assetMenu:
                self.sr.assetMenu.state = uiconst.UI_HIDDEN
            self.sr.tattooMenu.sr.mainCont.top = 0
            return self.sr.tattooMenu
        else:
            return self.ReloadTattooMenu()



    def ReloadTattooMenu(self, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::ReloadTattooMenu')
        self.StartLoadingThread()
        if self.sr.assetMenu:
            self.sr.assetMenu.state = uiconst.UI_HIDDEN
        if self.sr.tattooMenu:
            self.sr.tattooMenu.Close()
        info = self.GetInfo()
        piercingSub = (ccConst.p_brow,
         ccConst.p_nose,
         ccConst.p_nostril,
         ccConst.p_earshigh,
         ccConst.p_earslow,
         ccConst.p_lips,
         ccConst.p_chin)
        scarSub = (ccConst.s_head,)
        tattooSub = (ccConst.t_head,)
        groups = []
        groups += [(ccConst.PIERCINGGROUP, piercingSub)]
        groups += [(ccConst.TATTOOGROUP, tattooSub)]
        groups += [(ccConst.SCARSGROUP, scarSub)]
        tattoooMenuWidth = min(MAXMENUSIZE + uicls.CCColorPalette.COLORPALETTEWIDTH, self.sr.rightSide.width - 32)
        self.sr.tattooMenu = uicls.CharCreationAssetMenu(menuType='tattooMenu', parent=self.sr.assetMenuPar, bloodlineID=info.bloodlineID, state=uiconst.UI_PICKCHILDREN, genderID=info.genderID, charID=info.charID, groups=groups, align=uiconst.CENTERTOP, width=tattoooMenuWidth, height=uicore.desktop.height, top=16, toggleFunc=self.GoToAssetMode, togglerIdx=0)
        self.sr.tattooMenu.width = tattoooMenuWidth
        return self.sr.tattooMenu



    def GetAssetMenu(self, forcedMode = 0, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::GetAssetMenu')
        if not forcedMode and self.sr.assetMenu and not self.sr.assetMenu.destroyed:
            if self.sr.tattooMenu and not self.sr.tattooMenu.destroyed:
                self.sr.tattooMenu.state = uiconst.UI_HIDDEN
                self.sr.tattooMenu.sr.mainCont.height = uicore.desktop.height - self.sr.tattooMenu.top
            return self.sr.assetMenu
        else:
            return self.ReloadAssetMenu()



    def ReloadAssetMenu(self, *args):
        sm.GetService('cc').LogInfo('CharacterCustomization::ReloadAssetMenu')
        self.StartLoadingThread()
        if self.sr.assetMenu:
            self.sr.assetMenu.Close()
        if self.sr.tattooMenu:
            self.sr.tattooMenu.state = uiconst.UI_HIDDEN
        info = self.GetInfo()
        makeup = ccConst.MAKEUPGROUP
        if info.genderID == 1:
            makeup = ccConst.SKINDETAILSGROUP
        clothesSub = (ccConst.outer,
         ccConst.topouter,
         ccConst.topmiddle,
         ccConst.bottomouter,
         ccConst.feet,
         ccConst.glasses)
        groups = []
        if uicore.layer.charactercreation.CanChangeBaseAppearance():
            groups += [(ccConst.BODYGROUP, ())]
            groups += [(ccConst.SKINGROUP, ())]
        groups += [(ccConst.EYESGROUP, ())]
        groups += [(ccConst.HAIRGROUP, ())]
        groups += [(makeup, (ccConst.eyeshadow,
           ccConst.eyeliner,
           ccConst.blush,
           ccConst.lipstick))]
        groups += [(ccConst.CLOTHESGROUP, clothesSub)]
        assetMenuWidth = min(MAXMENUSIZE + uicls.CCColorPalette.COLORPALETTEWIDTH, self.sr.rightSide.width - 32)
        self.assetMenuMainWidth = assetMenuWidth - uicls.CCColorPalette.COLORPALETTEWIDTH
        self.sr.assetMenu = uicls.CharCreationAssetMenu(menuType='assetMenu', parent=self.sr.assetMenuPar, bloodlineID=info.bloodlineID, state=uiconst.UI_PICKCHILDREN, genderID=info.genderID, charID=info.charID, groups=groups, align=uiconst.CENTERTOP, width=assetMenuWidth, height=uicore.desktop.height, top=16, toggleFunc=self.GoToTattooMode)
        self.sr.assetMenuPar.width = assetMenuWidth
        if self.sr.historySlider:
            self.sr.historySlider.Close()
        self.sr.historySlider = uicls.CharacterCreationHistorySlider(parent=self.sr.uiContainer, align=uiconst.CENTERBOTTOM, top=-32, width=500, opacity=0.0, bitChangeCheck=self.IsDollReady, lastLitHistoryBit=uicore.layer.charactercreation.lastLitHistoryBit)
        self.sr.hintBox.left = self.assetMenuMainWidth + 20
        mask = service.ROLE_CONTENT | service.ROLE_QA | service.ROLE_PROGRAMMER | service.ROLE_GMH
        if eve.session.role & mask:
            if self.sr.debugReloadBtn:
                self.sr.debugReloadBtn.Close()
                self.sr.tattooModeBtn.Close()
            self.sr.debugReloadBtn = uicls.Button(parent=self.sr.uiContainer, func=self.GoToAssetMode, args=(0, 1), label='Reload Menu (debug)', align=uiconst.TOPRIGHT, left=self.sr.randomButton.left + 30, top=16)
            self.sr.tattooModeBtn = uicls.Button(parent=self.sr.uiContainer, func=self.GoToTattooMode, args=(0, 1), label='Go to Tattoo mode (debug)', align=uiconst.TOPRIGHT, left=250, top=16)
        uthread.new(uicore.effect.CombineEffects, self.sr.historySlider, top=42, opacity=1.0, time=125.0)
        return self.sr.assetMenu



    def GoToTattooMode(self, animate = 1, forcedMode = 0, *args):
        if not sm.StartService('device').SupportsSM3():
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/CharacterCreation/BodyModificationsNeedSM3')})
            return 
        self.menuMode = self.TATTOOMENU
        self.tattooChangeMade = 0
        self.charSvc.StopEditing()
        if self.sr.historySlider:
            self.sr.historySlider.state = uiconst.UI_HIDDEN
        self.sr.randomButton.Disable()
        if self.sr.assetMenu and not self.sr.assetMenu.destroyed:
            mainCont = self.sr.assetMenu.sr.mainCont
            h = mainCont.height - self.sr.assetMenu.sr.menuToggler.padTop
            h = mainCont.height - self.sr.assetMenu.sr.menuToggler.height - 4
            uicore.effect.MorphUIMassSpringDamper(mainCont, 'top', -h, newthread=False, float=False, frequency=15.0, dampRatio=0.85)
        self.LoadMenu(animate=animate, forcedMode=forcedMode)



    def GoToAssetMode(self, animate = 1, forcedMode = 0, *args):
        self.menuMode = self.ASSETMENU
        if self.sr.tattooMenu and not self.sr.tattooMenu.destroyed:
            if self.tattooChangeMade:
                uicore.layer.charactercreation.TryStoreDna(False, 'GoToAssetMode', sculpting=False, force=1, allowReduntant=0)
            mainCont = self.sr.tattooMenu.sr.mainCont
            h = self.sr.tattooMenu.sr.menuToggler.height + self.sr.tattooMenu.sr.menuToggler.padTop + self.sr.tattooMenu.sr.menuToggler.padBottom
            uicore.effect.CombineEffects(mainCont, height=h, time=250.0)
            uicore.effect.CombineEffects(mainCont, top=-8, time=10.0)
        self.tattooChangeMade = 0
        if uicore.layer.charactercreation.CanChangeBaseAppearance():
            uicore.layer.charactercreation.StartEditMode()
        if self.sr.historySlider:
            self.sr.historySlider.state = uiconst.UI_PICKCHILDREN
        self.sr.randomButton.Enable()
        self.LoadMenu(animate=1, forcedMode=forcedMode)



    def OnGenericMouseEnter(self, btn, *args):
        btn.sr.icon.SetAlpha(1.0)



    def OnGenericMouseExit(self, btn, *args):
        btn.sr.icon.SetAlpha(0.5)



    def LoadFaceMode(self, *args):
        info = self.GetInfo()
        avatar = self.charSvc.GetSingleCharactersAvatar(info.charID)
        uicore.layer.charactercreation.camera.ToggleMode(ccConst.CAMERA_MODE_FACE, avatar=avatar, transformTime=500.0)



    def LoadBodyMode(self, *args):
        info = self.GetInfo()
        avatar = self.charSvc.GetSingleCharactersAvatar(info.charID)
        uicore.layer.charactercreation.camera.ToggleMode(ccConst.CAMERA_MODE_BODY, avatar=avatar, transformTime=500.0)



    def ValidateStepComplete(self):
        info = self.GetInfo()
        if prefs.GetValue('ignoreCCValidation', False):
            return True
        if self.menuMode == self.TATTOOMENU:
            uicore.layer.charactercreation.TryStoreDna(False, 'ValidateStepComplete', force=1, allowReduntant=0)
        while not self.IsDollReady():
            blue.synchro.Yield()

        return self.charSvc.ValidateDollCustomizationComplete(info.charID)



    def ShowLoadingWheel_thread(self, *args):
        layer = uicore.layer.charactercreation
        doll = layer.doll
        while doll and not self.destroyed:
            if layer.sr.step and getattr(layer.sr.step, '_activeSculptZone', None) is not None:
                layer.HideLoading()
            elif doll.busyUpdating:
                layer.ShowLoading(why=localization.GetByLabel('UI/CharacterCreation/UpdatingCharacter'))
            else:
                layer.HideLoading()
            blue.pyos.synchro.SleepWallclock(100)




    def CheckAppFocus(self, wnd, msgID, vkey):
        focused = vkey[0]
        if not focused:
            uicore.layer.charactercreation.PassMouseEventToSculpt('LeftDown', uicore.uilib.x, uicore.uilib.y)
            uicore.layer.charactercreation.PassMouseEventToSculpt('LeftUp', uicore.uilib.x, uicore.uilib.y)
            self.ChangeSculptingCursor(-1, 0, 0)
        return 1



    def StoreHistorySliderPosition(self, *args):
        if self.sr.historySlider:
            (currentIndex, maxIndex,) = self.sr.historySlider.GetCurrentIndexAndMaxIndex()
        else:
            currentIndex = None
        uicore.layer.charactercreation.lastLitHistoryBit = currentIndex




class CharacterPortrait(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterPortrait'
    stepID = ccConst.PORTRAITSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.colorPaletteWidth = uicls.CCColorPalette.COLORPALETTEWIDTH
        self.portraitSize = 128
        self.selectedPortrait = 0
        self.sr.assetMenuPar = uicls.Container(parent=self.sr.rightSide, pos=(0,
         0,
         MAXMENUSIZE,
         uicore.desktop.height), state=uiconst.UI_PICKCHILDREN, align=uiconst.CENTERTOP)
        self.sr.hintBox = uicls.Container(parent=self.sr.assetMenuPar, pos=(MAXMENUSIZE,
         20,
         200,
         150), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
        self.sr.hintText = uicls.EveLabelMedium(text='', parent=self.sr.hintBox, align=uiconst.TOTOP)
        self.UpdateLayout()



    def UpdateLayout(self):
        BaseCharacterCreationStep.UpdateLayout(self)
        self.sr.rightSide.width += uicls.CCColorPalette.COLORPALETTEWIDTH
        self.ReloadPortraitAssetMenu()
        self.ReloadPortraits()
        self.sr.hintBox.left = self.assetMenuMainWidth + 20



    def ReloadPortraitAssetMenu(self):
        sm.GetService('cc').LogInfo('CharacterPortrait::ReloadPortraitAssetMenu')
        if self.sr.portraitAssetMenu:
            self.sr.portraitAssetMenu.Close()
        groups = [(ccConst.BACKGROUNDGROUP, ()), (ccConst.POSESGROUP, ()), (ccConst.LIGHTSGROUP, ())]
        assetMenuWidth = min(MAXMENUSIZE + uicls.CCColorPalette.COLORPALETTEWIDTH, self.sr.rightSide.width - 32)
        self.assetMenuMainWidth = assetMenuWidth - uicls.CCColorPalette.COLORPALETTEWIDTH
        self.sr.portraitAssetMenu = uicls.CharCreationAssetMenu(parent=self.sr.assetMenuPar, groups=groups, align=uiconst.CENTERTOP, width=assetMenuWidth, height=uicore.desktop.height, top=16)
        self.sr.assetMenuPar.width = assetMenuWidth



    def SetHintText(self, modifier, hintText = ''):
        text = hintText
        if modifier in ccConst.HELPTEXTS:
            labelPath = ccConst.HELPTEXTS[modifier]
            text = localization.GetByLabel(labelPath)
        if text != self.sr.hintText.text:
            self.sr.hintText.text = text



    def ReloadPortraits(self):
        if self.sr.portraitCont:
            self.sr.portraitCont.Close()
        self.sr.portraitCont = uicls.Container(name='portraitCont', parent=self.sr.leftSide, align=uiconst.CENTERTOP, pos=(0,
         128,
         128,
         134 * ccConst.NUM_PORTRAITS - 6 + 44))
        self.sr.facePortraits = [None] * ccConst.NUM_PORTRAITS
        for i in xrange(ccConst.NUM_PORTRAITS):
            if i == 0:
                frameAlpha = 0.8
            else:
                frameAlpha = 0.2
            portraitCont = uicls.Container(name='portraitCont1', parent=self.sr.portraitCont, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             self.portraitSize), padBottom=6, state=uiconst.UI_NORMAL)
            portraitCont.OnClick = (self.SetPortraitFocus, i)
            portraitCont.OnDblClick = self.OnPortraitDblClick
            portraitCont.OnMouseEnter = (self.OnPortraitEnter, portraitCont)
            button = uicls.Icon(parent=portraitCont, icon=ccConst.ICON_CAM_IDLE, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, color=ccConst.COLOR75, left=6, top=6)
            button._idleIcon = ccConst.ICON_CAM_IDLE
            button._pressedIcon = ccConst.ICON_CAM_PRESSED
            button._imageIndex = i
            button.OnClick = (self.CameraButtonClick, button)
            button.OnMouseEnter = (self.GenericButtonEnter, button)
            button.OnMouseExit = (self.GenericButtonExit, button)
            button.OnMouseDown = (self.GenericButtonDown, button)
            button.OnMouseUp = (self.GenericButtonUp, button)
            frame = uicls.Frame(parent=portraitCont, color=ccConst.COLOR + (frameAlpha,))
            facePortrait = uicls.Icon(parent=portraitCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            uicls.Fill(parent=portraitCont, color=(0.0, 0.0, 0.0, 0.35))
            portraitCont.sr.button = button
            portraitCont.sr.frame = frame
            portraitCont.sr.facePortrait = facePortrait
            portraitCont.hasPhoto = False
            self.sr.facePortraits[i] = portraitCont

        for i in xrange(ccConst.NUM_PORTRAITS):
            if uicore.layer.charactercreation.facePortraits[i] is not None:
                photo = uicore.layer.charactercreation.facePortraits[i]
                cont = self.sr.facePortraits[i]
                cont.sr.facePortrait.texture.atlasTexture = photo
                cont.sr.facePortrait.texture.atlasTexture.Reload()
                cont.hasPhoto = True
                cont.sr.button.state = uiconst.UI_HIDDEN
                if photo == uicore.layer.charactercreation.activePortrait:
                    self.SetPortraitFocus(i)

        btn = uicls.CharCreationButton(parent=self.sr.portraitCont, label=localization.GetByLabel('UI/CharacterCreation/ResetExpression'), pos=(0, 0, 0, 0), fixedwidth=128, align=uiconst.CENTERBOTTOM, func=self.ResetFacePose)



    def ResetFacePose(self, *args):
        info = self.GetInfo()
        self.charSvc.ResetFacePose(info.charID)



    def OnPortraitDblClick(self, *args):
        uicore.layer.charactercreation.Approve()



    def OnPortraitDblClick(self, *args):
        uicore.layer.charactercreation.Approve()



    def SetPortraitFocus(self, selectedNo, *args):
        self.selectedPortrait = selectedNo
        for portraitContainer in self.sr.facePortraits:
            portraitContainer.sr.frame.SetAlpha(0.2)
            portraitContainer.sr.facePortrait.SetAlpha(0.3)

        frame = self.sr.facePortraits[selectedNo].sr.frame
        frame.SetAlpha(0.8)
        portrait = self.sr.facePortraits[selectedNo].sr.facePortrait
        portrait.SetAlpha(1.0)
        uicore.layer.charactercreation.SetActivePortrait(selectedNo)



    def ValidateStepComplete(self):
        if not self.IsDollReady:
            return False
        if uicore.layer.charactercreation.GetPortraitInfo(self.selectedPortrait) is None:
            self.CapturePortrait(self.selectedPortrait)
        return True



    def CapturePortrait(self, idx, *args):
        photo = uicore.layer.charactercreation.CapturePortrait(idx)
        if photo:
            self.SetPortrait(photo)
            uicore.layer.charactercreation.SetFacePortrait(photo, idx)



    def SetPortrait(self, photo, *args):
        facePortraitCont = self.sr.facePortraits[self.selectedPortrait]
        facePortraitCont.sr.facePortrait.texture.atlasTexture = photo
        facePortraitCont.sr.facePortrait.texture.atlasTexture.Reload()
        facePortraitCont.hasPhoto = True



    def OnPortraitEnter(self, portrait, *args):
        portrait.sr.button.state = uiconst.UI_NORMAL
        portrait.sr.mouseOverTimer = base.AutoTimer(33.0, self.CheckPortraitMouseOver, portrait)



    def CheckPortraitMouseOver(self, portrait, *args):
        if uicore.uilib.mouseOver is portrait or uiutil.IsUnder(uicore.uilib.mouseOver, portrait):
            return 
        portrait.sr.mouseOverTimer = None
        if portrait.hasPhoto:
            portrait.sr.button.state = uiconst.UI_HIDDEN



    def CameraButtonClick(self, button, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_portrait_snapshot_play'))
        self.SetPortraitFocus(button._imageIndex)
        self.CapturePortrait(button._imageIndex)



    def GenericButtonDown(self, button, mouseBtn, *args):
        if mouseBtn == uiconst.MOUSELEFT:
            uiutil.MapIcon(button, button._pressedIcon)



    def GenericButtonUp(self, button, *args):
        uiutil.MapIcon(button, button._idleIcon)



    def GenericButtonEnter(self, button, *args):
        uiutil.MapIcon(button, button._idleIcon)



    def GenericButtonExit(self, button, *args):
        uiutil.MapIcon(button, button._idleIcon)




class CharacterNaming(BaseCharacterCreationStep):
    __guid__ = 'uicls.CharacterNaming'
    __notifyevents__ = ['OnHideUI', 'OnShowUI']
    stepID = ccConst.NAMINGSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.isSerenity = boot.region == 'optic'
        self.namesChecked = {}
        self.schoolInfo = {}
        self.ancestryInfo = {}
        self.ancestryConts = {}
        self.schoolConts = {}
        self.checkingName = 0
        self.startAncestryHeight = 180
        self.startEducationHeight = 180
        self.padding = 16
        self.SetupAncestrySection()
        self.SetupEducationSection()
        self.SetupNameSection()
        self.sr.portraitCont = uicls.Container(name='portraitCont', parent=self.sr.leftSide, align=uiconst.CENTERTOP, pos=(0, 128, 128, 128))
        uicls.Frame(parent=self.sr.portraitCont, color=ccConst.COLOR + (0.3,))
        self.sr.facePortrait = uicls.Icon(parent=self.sr.portraitCont, idx=1, align=uiconst.TOALL)
        photo = uicore.layer.charactercreation.GetActivePortrait()
        if photo is not None:
            self.sr.facePortrait.texture.atlasTexture = photo
            self.sr.facePortrait.texture.atlasTexture.Reload()
        self.UpdateLayout()



    def UpdateLayout(self):
        BaseCharacterCreationStep.UpdateLayout(self)
        info = self.GetInfo()
        self.sr.rightSide.width = min(self.sr.rightSide, 380)
        picker = uicls.CCRacePicker(parent=self.sr.leftSide, align=uiconst.BOTTOMLEFT, owner=self, raceID=info.raceID, bloodlineID=info.bloodlineID, genderID=info.genderID, padding=(30, 0, 0, 0), clickable=False, showText=True)
        self.AdjustHeightAndWidth(doMorph=0)
        try:
            self.SetAncestryFromID(info.ancestryID, doMorph=0)
            self.SetSchoolFromID(info.schoolID, doMorph=0)
        except Exception:
            if self and not self.destroyed:
                raise 



    def SetupAncestrySection(self, *args):
        info = self.GetInfo()
        padding = self.padding
        if self.sr.ancestyCont:
            self.sr.ancestyCont.Close()
        self.sr.ancestyCont = uicls.Container(name='ancestryCont', parent=self.sr.rightSide, align=uiconst.TOTOP, height=self.startAncestryHeight, padding=(padding,
         padding,
         padding,
         0))
        sub = uicls.Container(name='sub', parent=self.sr.ancestyCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=(padding,
         padding,
         padding,
         padding))
        topCont = uicls.Container(name='topCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0, 30, 0, 78))
        text = uicls.CCLabel(parent=sub, text=localization.GetByLabel('UI/CharacterCreation/AncestrySelection'), fontsize=20, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, -6, 0, 0), uppercase=1, color=ccConst.COLOR50)
        self.ancestryTextCont = textCont = uicls.Container(name='textCont', parent=sub, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.ancestryNameText = uicls.CCLabel(parent=textCont, text='', fontsize=14, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, 0, 0, 0), color=ccConst.COLOR50)
        self.sr.ancestryDescrText = uicls.CCLabel(parent=textCont, text='', fontsize=10, align=uiconst.TOTOP, letterspace=0, idx=1, padTop=20, shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
        hiliteFrame = uicls.Frame(name='hiliteFrame', parent=self.sr.ancestyCont, frameConst=ccConst.MAINFRAME_INV)
        uicls.Fill(name='fill', parent=self.sr.ancestyCont, color=(0.0, 0.0, 0.0, 0.5))
        if not self.ancestryInfo:
            ancestries = sm.GetService('cc').GetData('ancestries', ['bloodlineID', info.bloodlineID], 1)
            for each in ancestries:
                self.ancestryInfo[each.ancestryID] = each

        self.ancestryConts = {}
        left = 0
        for (i, (ancestryID, info,),) in enumerate(self.ancestryInfo.iteritems()):
            c = uicls.Container(name='c', parent=topCont, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pos=(left,
             0,
             100,
             80))
            hexName = localization.GetByMessageID(info.ancestryNameID)
            label = uicls.CCLabel(parent=c, text='<center>%s' % hexName, fontsize=12, align=uiconst.CENTERTOP, letterspace=0, idx=1, pos=(0,
             46,
             c.width,
             0), shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
            hex = uicls.CCHexButtonAncestry(name='ancestryHex', parent=c, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, -10, 64, 64), pickRadius=32, info=info, id=ancestryID, hexName=hexName, func=self.SetAncestry, iconNum=ancestryID - 1)
            left += 110
            self.ancestryConts[ancestryID] = hex




    def SetAncestryFromID(self, ancestryID, doMorph = 1, *args):
        selected = self.ancestryConts.get(ancestryID, None)
        self.SetAncestry(selected, doMorph=doMorph)



    def SetAncestry(self, selected = None, doMorph = 1, *args):
        if selected is None:
            i = random.randint(0, 2)
            selected = self.ancestryConts.values()[i]
        uicore.layer.charactercreation.SelectAncestry(selected.id)
        selected.SelectHex(self.ancestryConts.values())
        ancestryInfo = self.ancestryInfo.get(selected.id)
        self.sr.ancestryNameText.text = localization.GetByMessageID(ancestryInfo.ancestryNameID)
        self.sr.ancestryDescrText.text = localization.GetByMessageID(ancestryInfo.descriptionID)
        selected.frame.state = uiconst.UI_DISABLED
        self.AdjustHeightAndWidth(doMorph=doMorph)



    def SetupEducationSection(self, *args):
        info = self.GetInfo()
        padding = self.padding
        if self.sr.educationCont:
            self.sr.educationCont.Close()
        self.sr.educationCont = uicls.Container(name='educationCont', parent=self.sr.rightSide, align=uiconst.TOTOP, height=self.startEducationHeight, padding=(padding,
         padding,
         padding,
         0))
        sub = uicls.Container(name='sub', parent=self.sr.educationCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=(padding,
         padding,
         padding,
         padding))
        topCont = uicls.Container(name='topCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0, 30, 0, 78))
        text = uicls.CCLabel(parent=sub, text=localization.GetByLabel('UI/CharacterCreation/EducationSelection'), fontsize=20, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, -6, 0, 0), uppercase=1, color=ccConst.COLOR50)
        self.schoolTextCont = textCont = uicls.Container(name='textCont', parent=sub, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.schoolNameText = uicls.CCLabel(parent=textCont, text='', fontsize=14, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, 0, 0, 0), color=ccConst.COLOR50)
        self.sr.schoolDescrText = uicls.CCLabel(parent=textCont, text='', fontsize=10, align=uiconst.TOTOP, letterspace=0, idx=1, padTop=20, shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
        hiliteFrame = uicls.Frame(name='hiliteFrame', parent=self.sr.educationCont, frameConst=ccConst.MAINFRAME_INV)
        uicls.Fill(name='fill', parent=self.sr.educationCont, color=(0.0, 0.0, 0.0, 0.5))
        if not self.schoolInfo:
            schools = sm.GetService('cc').GetData('schools', ['raceID', info.raceID], 1)
            for each in schools:
                info = sm.GetService('cc').GetData('schools', ['schoolID', each.schoolID])
                self.schoolInfo[each.schoolID] = info

        left = 0
        offsetByRace = {const.raceCaldari: 17,
         const.raceMinmatar: 14,
         const.raceAmarr: 11,
         const.raceGallente: 20}
        iconNumOffset = offsetByRace.get(info.raceID)
        for (schoolID, info,) in self.schoolInfo.iteritems():
            c = uicls.Container(name='c', parent=topCont, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pos=(left,
             0,
             100,
             80))
            hexName = localization.GetByMessageID(info.schoolNameID)
            label = uicls.CCLabel(parent=c, text='<center>%s' % hexName, fontsize=12, align=uiconst.CENTERTOP, letterspace=0, idx=1, pos=(0,
             46,
             c.width,
             0), shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
            hex = uicls.CCHexButtonSchool(name='schoolHex', parent=c, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, -10, 64, 64), pickRadius=32, info=info, id=schoolID, hexName=hexName, func=self.SetSchool, iconNum=schoolID - iconNumOffset)
            left += 110
            self.schoolConts[schoolID] = hex




    def SetSchoolFromID(self, schoolID, doMorph = 1, *args):
        selected = self.schoolConts.get(schoolID, None)
        self.SetSchool(selected, doMorph=doMorph)



    def SetSchool(self, selected = None, doMorph = 1, *args):
        if selected is None:
            i = random.randint(0, 2)
            selected = self.schoolConts.values()[i]
        uicore.layer.charactercreation.SelectSchool(selected.id)
        selected.SelectHex(self.schoolConts.values())
        schoolInfo = self.schoolInfo.get(selected.id)
        self.sr.schoolNameText.text = selected.hexName
        self.sr.schoolDescrText.text = localization.GetByMessageID(schoolInfo.descriptionID)
        selected.frame.state = uiconst.UI_DISABLED
        self.AdjustHeightAndWidth(doMorph=doMorph)



    def SetupNameSection(self, *args):
        info = self.GetInfo()
        padding = self.padding
        if self.sr.nameCont:
            self.sr.nameCont.Close()
        if self.isSerenity:
            maxFirstNameChars = 37
            contHeight = 120
        else:
            maxFirstNameChars = 24
            contHeight = 160
        self.sr.nameCont = uicls.Container(name='nameCont', parent=self.sr.rightSide, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         contHeight), padding=(padding,
         padding,
         padding,
         0))
        if not uicore.layer.charactercreation.CanChangeName():
            self.sr.nameCont.height = 0
            return 
        sub = uicls.Container(name='sub', parent=self.sr.nameCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=(padding,
         padding,
         padding,
         padding))
        hiliteFrame = uicls.Frame(name='hiliteFrame', parent=self.sr.nameCont, frameConst=ccConst.MAINFRAME_INV)
        uicls.Fill(name='fill', parent=self.sr.nameCont, color=(0.0, 0.0, 0.0, 0.5))
        text = uicls.CCLabel(parent=sub, text=localization.GetByLabel('UI/CharacterCreation/NameSelection'), fontsize=20, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, -6, 0, 0), uppercase=1, color=ccConst.COLOR50)
        text.SetRGB(1.0, 1.0, 1.0)
        text.SetAlpha(1.0)
        top = 30
        firstName = info.charFirstName or ''
        self.sr.firstNameEdit = edit = uicls.SinglelineEdit(name='firstNameEdit', setvalue=firstName, parent=sub, pos=(4,
         top,
         150,
         0), maxLength=maxFirstNameChars, align=uiconst.TOTOP, OnChange=self.EnteringName, color=(1.0, 1.0, 1.0, 1.0), hinttext=localization.GetByLabel('UI/CharacterCreation/FirstName'))
        edit.OnReturn = self.CheckAvailability
        edit.OnAnyChar = self.OnCharInFirstName
        offset = 20
        if not self.isSerenity:
            btnTop = edit.top + edit.height + offset - 2
            btn = uicls.CharCreationButton(parent=sub, label=localization.GetByLabel('UI/CharacterCreation/Randomize'), pos=(0,
             btnTop,
             0,
             0), align=uiconst.TOPRIGHT, func=self.RandomizeLastName)
            rightPadding = btn.width + 10
            lastNameEditCont = uicls.Container(name='lastNameEditCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0,
             offset - 10,
             0,
             29), padding=(0,
             0,
             rightPadding,
             0))
            lastNameEditCont.isTabOrderGroup = 1
            lastName = info.charLastName or ''
            self.sr.lastNameEdit = edit = uicls.SinglelineEdit(name='lastNameEdit', parent=lastNameEditCont, setvalue=lastName, pos=(0, 10, 0, 0), maxLength=12, align=uiconst.TOTOP, OnChange=self.EnteringName, color=(1.0, 1.0, 1.0, 1.0), hinttext=localization.GetByLabel('UI/CharacterCreation/LastName'))
            edit.OnReturn = self.CheckAvailability
            edit.OnAnyChar = self.OnCharInLastName
            self.sr.firstNameEdit.padRight = rightPadding
        availCont = uicls.Container(name='availCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0,
         offset,
         0,
         0))
        availBtn = uicls.CharCreationButton(parent=availCont, label=localization.GetByLabel('UI/CharacterCreation/CheckNameAvailability'), pos=(0, 0, 0, 0), align=uiconst.TOPLEFT, func=self.CheckAvailability)
        availCont.height = availBtn.height
        left = availBtn.width + 4
        self.sr.availabilityLabel = uicls.EveLabelMedium(parent=availCont, align=uiconst.CENTERLEFT, left=left + 16, state=uiconst.UI_DISABLED)
        self.sr.availableIcon = uicls.Icon(parent=availCont, align=uiconst.CENTERLEFT, pos=(left,
         0,
         16,
         16), state=uiconst.UI_HIDDEN)
        self.sr.availableIcon.LoadIcon('ui_38_16_193')



    def RandomizeLastName(self, *args):
        info = self.GetInfo()
        self.sr.lastNameEdit.SetValue(uicore.layer.charactercreation.GetRandomLastName(info.bloodlineID))



    def EnteringName(self, *args):
        self.sr.availabilityLabel.state = uiconst.UI_HIDDEN
        self.sr.availableIcon.state = uiconst.UI_HIDDEN



    def OnCharInFirstName(self, char, *args):
        if char == uiconst.VK_SPACE:
            if self.isSerenity:
                allowedNumSpaces = 2
            else:
                allowedNumSpaces = 1
            numSpaces = self.sr.firstNameEdit.text.count(' ')
            if numSpaces >= allowedNumSpaces:
                uicore.Message('uiwarning03')
                return False
        return True



    def OnCharInLastName(self, char, *args):
        if char == uiconst.VK_SPACE:
            uicore.Message('uiwarning03')
            return False
        return True



    def CheckAvailability(self, *args):
        if self.checkingName:
            return 
        else:
            self.checkingName = 1
            charFirstName = self.sr.firstNameEdit.GetValue()
            if self.isSerenity:
                charLastName = ''
            else:
                charLastName = self.sr.lastNameEdit.GetValue()
                self.sr.lastNameEdit.CloseHistoryMenu()
            self.sr.firstNameEdit.CloseHistoryMenu()
            charName = charFirstName
            if charLastName:
                charName += ' %s' % charLastName
            if charName in self.namesChecked:
                valid = self.namesChecked[charName]
            else:
                valid = sm.RemoteSvc('charUnboundMgr').ValidateNameEx(charName)
                self.namesChecked[charName] = valid
            self.sr.availableIcon.state = uiconst.UI_DISABLED
            self.sr.availabilityLabel.state = uiconst.UI_DISABLED
            isAvailable = util.KeyVal()
            self.checkingName = 0
            if valid == 1:
                self.sr.availableIcon.LoadIcon('ui_38_16_193')
                self.sr.availabilityLabel.text = ''
                isAvailable.charName = charName
                isAvailable.reason = ''
                uicore.layer.charactercreation.charFirstName = charFirstName
                uicore.layer.charactercreation.charLastName = charLastName
                return isAvailable
            validStates = {-1: localization.GetByLabel('UI/CharacterCreation/InvalidName/TooShort'),
             -2: localization.GetByLabel('UI/CharacterCreation/InvalidName/TooLong'),
             -5: localization.GetByLabel('UI/CharacterCreation/InvalidName/IllegalCharacter'),
             -6: localization.GetByLabel('UI/CharacterCreation/InvalidName/TooManySpaces'),
             -7: localization.GetByLabel('UI/CharacterCreation/InvalidName/ConsecutiveSpaces'),
             -101: localization.GetByLabel('UI/CharacterCreation/InvalidName/Unavailable'),
             -102: localization.GetByLabel('UI/CharacterCreation/InvalidName/Unavailable')}
            reason = validStates.get(valid, localization.GetByLabel('UI/CharacterCreation/InvalidName/IllegalCharacter'))
            self.sr.availableIcon.LoadIcon('ui_38_16_194')
            self.sr.availabilityLabel.text = reason
            if not self.isSerenity:
                self.sr.lastNameEdit.SelectAll()
                uicore.registry.SetFocus(self.sr.lastNameEdit)
            isAvailable.charName = None
            isAvailable.reason = reason
            return isAvailable



    def AdjustHeightAndWidth(self, doMorph = 1, *args):
        schoolTextContHeight = self.sr.educationCont.height - 130
        textHeight = self.sr.schoolDescrText.textheight + self.sr.schoolDescrText.padTop
        missingSchoolHeight = textHeight - schoolTextContHeight
        ancestryTextContHeight = self.sr.ancestyCont.height - 130
        textHeight = self.sr.ancestryDescrText.textheight + self.sr.ancestryDescrText.padTop
        missingAncestryHeight = textHeight - ancestryTextContHeight
        totalMissing = max(missingSchoolHeight, 0) + max(missingAncestryHeight, 0)
        if totalMissing > 0:
            for (missingHeight, cont,) in [(missingSchoolHeight, self.sr.educationCont), (missingAncestryHeight, self.sr.ancestyCont)]:
                if missingHeight < -10:
                    cont.height -= 5
                    blue.synchro.Yield()
                    if self and not self.destroyed:
                        self.AdjustHeightAndWidth(doMorph=doMorph)
                    return 

            availableHeight = uicore.desktop.height - self.sr.ancestyCont.height - self.sr.educationCont.height - self.sr.nameCont.height - 80 - 4 * self.padding
            if availableHeight >= totalMissing:
                if missingSchoolHeight > 0:
                    self.sr.educationCont.height += missingSchoolHeight + 2
                if missingAncestryHeight > 0:
                    self.sr.ancestyCont.height += missingAncestryHeight + 2
            elif self.sr.rightSide.width < uicore.desktop.width * 0.6:
                if doMorph:
                    uicore.effect.CombineEffects(self.sr.rightSide, width=self.sr.rightSide.width + 50, time=25)
                else:
                    self.sr.rightSide.width += 50
                    blue.synchro.Yield()
                self.AdjustHeightAndWidth(doMorph=doMorph)




class CharCreationButton(uicls.ButtonCore):
    __guid__ = 'uicls.CharCreationButton'
    default_align = uiconst.TOPLEFT

    def Prepare_(self):
        self.sr.label = uicls.Label(parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, bold=1, uppercase=0, idx=0, fontsize=self.default_fontsize, color=ccConst.COLOR + (TEXT_NORMAL,), letterspace=1)
        self.sr.hilite = uicls.Frame(parent=self, name='hilite', state=uiconst.UI_HIDDEN, color=ccConst.COLOR + (0.2,), frameConst=ccConst.FILL_BEVEL)
        self.sr.hilite.padLeft = self.sr.hilite.padTop = self.sr.hilite.padRight = self.sr.hilite.padBottom = 3
        fill = uicls.Fill(parent=self, name='fill', state=uiconst.UI_DISABLED, color=(0.35, 0.35, 0.35, 0.3), padding=(2, 2, 2, 2))
        self.sr.activeframe = uicls.Fill(parent=self, name='activeframe', state=uiconst.UI_HIDDEN, color=ccConst.COLOR + (FILL_SELECTION,), padding=(2, 2, 2, 2))
        hiliteFrame = uicls.Frame(name='hiliteFrame', parent=self, frameConst=('ui_105_32_10', 8, -2), color=(1.0, 1.0, 1.0, 0.4))
        shadow = uicls.Frame(name='shadow', parent=self, frameConst=ccConst.FRAME_SOFTSHADE)
        shadow.SetPadding(-9, -6, -9, -11)



    def Update_Size_(self):
        uicls.ButtonCore.Update_Size_(self)
        self.height = 25



    def OnSetFocus(self, *args):
        uicls.ButtonCore.OnSetFocus(self, *args)
        self.sr.label.SetAlpha(1.0)



    def OnKillFocus(self, *args):
        uicls.ButtonCore.OnKillFocus(self, *args)
        self.sr.label.SetAlpha(TEXT_NORMAL)



    def OnMouseEnter(self, *args):
        uicls.ButtonCore.OnMouseEnter(self, *args)
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))



    def OnClick(self, *blah):
        if not self or self.destroyed:
            return 
        if not self.func:
            return 
        if type(self.args) == tuple:
            self.func(*self.args)
        else:
            self.func(self.args or self)
        if not self.destroyed and self.sr.hilite and uicore.uilib.mouseOver != self and not self.blinking:
            self.Hilite_(False)
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))




class CCLabel(uicls.Label):
    __guid__ = 'uicls.CCLabel'
    default_bold = 1
    default_color = ccConst.COLOR
    default_letterspace = 1
    default_state = uiconst.UI_DISABLED


class CCHeadBodyPicker(uicls.Container):
    __guid__ = 'uicls.CCHeadBodyPicker'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.headCallback = attributes.headCallback
        self.bodyCallback = attributes.bodyCallback
        self.Setup()



    def Setup(self, *args):
        self.width = 130
        self.height = 130
        self.SetOpacity(0.0)
        hex = uicls.CCHexButtonHead(name='headHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64), pickRadius=21, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomIn'), func=self.HeadClicked, iconNum=0, showIcon=False)
        self.sr.headSolid = hex.selection
        hex.selection.state = uiconst.UI_DISABLED
        self.sr.headFrame = hex.frame
        self.sr.headHex = hex
        hex = uicls.CCHexButtonBody(name='bodyHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 16, 128, 128), pickRadius=42, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomOut'), func=self.BodyClicked, iconNum=0, showIcon=False)
        self.sr.bodySolid = hex.selection
        hex.selection.state = uiconst.UI_DISABLED
        self.sr.bodyFrame = hex.frame
        self.sr.bodyHex = hex
        texturePath = 'res:/UI/Texture/CharacterCreation/silhuette_ghost.dds'
        sprite = uicls.Sprite(name='ghost', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 7, 128, 128), idx=0, texturePath=texturePath)
        (sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight,) = (0, 0, 0, 0)
        self.sr.updateTimer = base.AutoTimer(33, self.UpdatePosition)
        uthread.new(uicore.effect.CombineEffects, self, opacity=1.0, time=250.0)



    def UpdatePosition(self, *args):
        if self.destroyed:
            return 
        camera = getattr(uicore.layer.charactercreation, 'camera', None)
        if camera is not None:
            portion = camera.GetPortionFromDistance()
            self.sr.headSolid.SetOpacity(max(0.2, 1.0 - portion))
            self.sr.bodySolid.SetOpacity(max(0.2, portion))
            for hex in (self.sr.headHex, self.sr.bodyHex):
                if hex.selection.opacity >= 0.5 and len(self.children) and hex == self.children[-1]:
                    toSwap = self.children[-2]
                    self.children.remove(toSwap)
                    self.children.append(toSwap)
                    break




    def MouseOverPart(self, frameName, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))
        frame = self.sr.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_DISABLED



    def MouseExitPart(self, frameName, *args):
        frame = self.sr.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_HIDDEN



    def HeadClicked(self, *args):
        self.sr.headFrame.state = uiconst.UI_HIDDEN
        self.sr.bodyFrame.state = uiconst.UI_HIDDEN
        if self.headCallback:
            self.headCallback()



    def BodyClicked(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
        self.sr.headFrame.state = uiconst.UI_HIDDEN
        self.sr.bodyFrame.state = uiconst.UI_HIDDEN
        if self.bodyCallback:
            self.bodyCallback()




class BitSlider(uicls.Container):
    __guid__ = 'uicls.BitSlider'
    default_name = 'BitSlider'
    default_align = uiconst.RELATIVE
    default_bitWidth = 3
    default_bitHeight = 8
    default_bitGap = 1
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 12
    cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.onSetValueCallback = None
        targetWidth = attributes.get('sliderWidth', 100)
        bitGap = attributes.get('bitGap', self.default_bitGap)
        bitAmount = attributes.bitAmount
        self.bitHeight = attributes.bitHeight or self.default_bitHeight
        self.height = self.bitHeight + 4
        if bitAmount:
            self.bitWidth = int(targetWidth / float(bitAmount))
        else:
            self.bitWidth = attributes.bitWidth or self.default_bitWidth
        self._value = 0.0
        self.sr.handle = uicls.Container(parent=self, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, pos=(0,
         0,
         3,
         self.height))
        uicls.Fill(parent=self.sr.handle, color=ccConst.COLOR + (1.0,))
        i = 0
        while True:
            if bitAmount is None and i >= 3 and i * (self.bitWidth + bitGap) + self.bitWidth > targetWidth:
                break
            bit = uicls.Container(parent=self, pos=(i * (self.bitWidth + bitGap),
             2,
             self.bitWidth,
             self.bitHeight), align=uiconst.RELATIVE, state=uiconst.UI_DISABLED)
            bit.isBit = True
            uicls.Fill(parent=bit, color=ccConst.COLOR + (1.0,))
            i += 1
            if bitAmount is not None and i == bitAmount:
                break

        self._numBits = i
        if targetWidth != bit.left + bit.width:
            diff = targetWidth - (bit.left + bit.width)
            bit.width += diff
        self.width = targetWidth
        if attributes.setvalue is not None:
            self.SetValue(attributes.setvalue)
        self.onSetValueCallback = attributes.OnSetValue



    def OnMouseDown(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return 
        self.sr.softSlideTimer = None
        self.sr.slideTimer = base.AutoTimer(33, self.UpdateSliderPortion)



    def OnMouseEnter(self, *args):
        self.sr.softSlideTimer = base.AutoTimer(33, self.UpdateSoftSliderPortion)



    def OnMouseExit(self, *args):
        pass



    def OnMouseWheel(self, *args):
        if uicore.uilib.dz > 0:
            self.SetValue(self.GetValue() + 1.0 / self._numBits)
        else:
            self.SetValue(self.GetValue() - 1.0 / self._numBits)



    def UpdateSoftSliderPortion(self, *args):
        if uicore.uilib.mouseOver is self or uiutil.IsUnder(uicore.uilib.mouseOver, self):
            (l, t, w, h,) = self.GetAbsolute()
            portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
            self.ShowSoftLit(portion)
        else:
            self.sr.softSlideTimer = None
            self.ShowSoftLit(0.0)



    def UpdateSliderPortion(self, *args):
        (l, t, w, h,) = self.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.sr.handle.left = int((w - self.bitWidth) * portion)
        self.ShowLit(portion)



    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return 
        self.sr.slideTimer = None
        (l, t, w, h,) = self.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.sr.handle.left = int((w - self.sr.handle.width) * portion)
        self.SetValue(portion)



    def ShowLit(self, portion):
        (l, t, w, h,) = self.GetAbsolute()
        if not w:
            return 
        self.sr.handle.left = int((w - self.sr.handle.width) * portion)
        for each in self.children:
            if not hasattr(each, 'isBit'):
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(1.0)
            else:
                each.SetOpacity(0.333)




    def ShowSoftLit(self, portion):
        (l, t, w, h,) = self.GetAbsolute()
        for each in self.children:
            if not hasattr(each, 'isBit'):
                continue
            if each.opacity == 1.0:
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(0.5)
            else:
                each.SetOpacity(0.333)




    def SetValue(self, value, doCallback = True):
        callback = value != self._value
        self._value = max(0.0, min(1.0, value))
        self.ShowLit(self._value)
        if callback and doCallback and self.onSetValueCallback:
            self.onSetValueCallback(self)



    def GetValue(self):
        return self._value




class BaseCCButton(uicls.Container):
    __guid__ = 'uicls.BaseCCButton'
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 128
    default_align = uiconst.CENTER
    mouseoverSound = 'wise:/ui_icc_button_mouse_over_play'
    selectSound = 'wise:/ui_icc_button_select_play'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.normalSprite = uicls.Sprite(name='normalSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='', width=self.default_width, height=self.default_height)
        self.hiliteSprite = uicls.Sprite(name='hiliteSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, texturePath='', width=self.default_width, height=self.default_height)
        self.normalSprite.SetAlpha(0.3)



    def OnMouseEnter(self, *args):
        sm.StartService('audio').SendUIEvent(unicode(self.mouseoverSound))
        self.normalSprite.SetAlpha(0.6)



    def OnMouseExit(self, *args):
        self.normalSprite.SetAlpha(0.3)



    def Deselect(self):
        self.hiliteSprite.state = uiconst.UI_HIDDEN
        self.normalSprite.state = uiconst.UI_DISABLED



    def Select(self):
        sm.StartService('audio').SendUIEvent(unicode(self.selectSound))
        self.hiliteSprite.state = uiconst.UI_DISABLED
        self.normalSprite.state = uiconst.UI_HIDDEN



    def OnClick(self, *args):
        pass




class RaceButton(BaseCCButton):
    __guid__ = 'uicls.RaceButton'
    default_left = 0
    default_top = 0
    default_width = 256
    default_height = 256

    def ApplyAttributes(self, attributes):
        uicls.BaseCCButton.ApplyAttributes(self, attributes)
        self.raceID = attributes.raceID
        self.normalSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/raceButtons/RaceButtonNormal_%s.dds' % self.raceID
        self.hiliteSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/raceButtons/RaceButtonDown_%s.dds' % self.raceID



    def OnMouseEnter(self, *args):
        uicls.BaseCCButton.OnMouseEnter(self, *args)
        info = uicore.layer.charactercreation.GetInfo()
        if not info.raceID:
            uicore.layer.charactercreation.UpdateBackdropLite(raceID=self.raceID, mouseEnter=True)



    def OnMouseExit(self, *args):
        uicls.BaseCCButton.OnMouseExit(self, *args)
        info = uicore.layer.charactercreation.GetInfo()
        if not info.raceID:
            uicore.layer.charactercreation.UpdateBackdropLite(raceID=None, mouseEnter=True)



    def OnClick(self, *args):
        if uicore.layer.charactercreation.raceID != self.raceID:
            uicore.layer.charactercreation.SelectRace(self.raceID)



    def OnDblClick(self, *args):
        uicore.layer.charactercreation.Approve()




class BloodlineButton(BaseCCButton):
    __guid__ = 'uicls.BloodlineButton'

    def ApplyAttributes(self, attributes):
        uicls.BaseCCButton.ApplyAttributes(self, attributes)
        self.bloodlineID = attributes.bloodlineID
        self.normalSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Bloodline_Normal_%d.dds' % self.bloodlineID
        self.hiliteSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Bloodline_Down_%d.dds' % self.bloodlineID



    def OnClick(self, *args):
        if uicore.layer.charactercreation.bloodlineID != self.bloodlineID:
            uicore.layer.charactercreation.SelectBloodline(self.bloodlineID)




class GenderButton(BaseCCButton):
    __guid__ = 'uicls.GenderButton'
    default_left = 0
    default_top = 0
    default_width = 64
    default_height = 64
    selectSound = 'wise:/ui_icc_button_select_gender_play'

    def ApplyAttributes(self, attributes):
        uicls.BaseCCButton.ApplyAttributes(self, attributes)
        self.raceID = attributes.raceID
        self.genderID = attributes.genderID
        if self.genderID == ccConst.GENDERID_FEMALE:
            gender = 'Female'
        else:
            gender = 'Male'
        self.normalSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Gender_%s_Normal.dds' % gender
        self.hiliteSprite.texture.resPath = 'res:/UI/Texture/CharacterCreation/bloodlineButtons/Gender_%s_%d.dds' % (gender, self.raceID)



    def OnClick(self, *args):
        if uicore.layer.charactercreation.genderID != self.genderID:
            uicore.layer.charactercreation.SelectGender(self.genderID)



    def OnDblClick(self, *args):
        uicore.layer.charactercreation.Approve()




