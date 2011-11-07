import uicls
import uiutil
import uiconst
import uix
import trinity
import GameWorld
import uthread
import blue
import cameras
import paperDoll
import util
import copy
import ccUtil
import ccConst
import random
import log
import types
import bluepy
import math
import geo2
import form
import service
import paperDollUtil
from sceneManager import SCENE_TYPE_INTERIOR
MINSIDESIZE = 200
LEFTSIZE = 200
RIGHTSIZE = 350
SKINTONE_BASE_COLOR_PATH = 'res:/Graphics/Character/Modular/Female/Skintone/Basic/'
DOLLSTATES_TO_RETURN_TO_CC = [const.paperdollStateNoExistingCustomization, const.paperdollStateForceRecustomize]

class CharacterCreationLayer(uicls.LayerCore):
    __guid__ = 'uicls.CharacterCreationLayer'
    __notifyevents__ = ['OnSetDevice',
     'OnGraphicSettingsChanged',
     'OnHideUI',
     'OnShowUI',
     'OnDollUpdated',
     'OnMapShortcut']

    @bluepy.CCP_STATS_ZONE_METHOD
    def OnSetDevice(self, *args):
        self.UpdateLayout()
        self.UpdateBackdrop()
        if self.stepID == ccConst.BLOODLINESTEP:
            self.CorrectBloodlinePlacement()



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateLayout(self):
        for each in self.sr.mainCont.children:
            if hasattr(each, 'UpdateLayout'):
                each.UpdateLayout()




    @bluepy.CCP_STATS_ZONE_METHOD
    def OnOpenView(self):
        uicore.cmd.commandMap.UnloadAllAccelerators()
        uicore.cmd.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_GENERAL)
        sm.GetService('tutorial').ChangeTutorialWndState(visible=False)
        if hasattr(trinity, 'InitializeApex'):
            trinity.InitializeApex(GameWorld.GWPhysXWrapper())
        self._setColorsByCategory = {}
        self._setSpecularityByCategory = {}
        self._setIntensityByCategory = {}
        self.characterSvc = sm.GetService('character')
        self.backdropPath = None
        self.posePath = None
        self.lightingID = ccConst.LIGHT_SETTINGS_ID[0]
        self.lightColorID = ccConst.LIGHT_COLOR_SETTINGS_ID[0]
        self.lightIntensity = 0.5
        self.camera = None
        self.cameraUpdateJob = None
        self.fastCharacterCreation = prefs.GetValue('fastCharacterCreation', 0)
        self.bloodlineSelector = None
        self.raceMusicStarted = False
        self.jukeboxWasPlaying = False
        self.worldLevel = sm.GetService('audio').GetWorldVolume()
        sm.GetService('audio').SetWorldVolume(0.0)
        self.mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        self.charID = None
        self.raceID = None
        self.bloodlineID = None
        self.genderID = None
        self.ancestryID = None
        self.schoolID = None
        self.charFirstName = ''
        self.charLastName = ''
        self.clothesOff = 0
        self.clothesStorage = {}
        self.dnaList = None
        self.dna = None
        self.lastLitHistoryBit = None
        sm.GetService('cc').ClearMyAvailabelTypeIDs()
        self.stepID = None
        self.floor = None
        self.showingHelp = 0
        self.sr.loadingWheel = uicls.LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        self.sr.loadingWheel.forcedOn = 0
        self.sr.uiContainer = uicls.Container(name='uiContainer', parent=self, align=uiconst.TOALL)
        self.sr.leftSide = uicls.Container(name='leftSide', parent=self.sr.uiContainer, align=uiconst.TOPLEFT, pos=(0,
         0,
         LEFTSIZE,
         400))
        self.sr.rightSide = uicls.Container(name='rightSide', parent=self.sr.uiContainer, align=uiconst.BOTTOMRIGHT, pos=(0,
         0,
         RIGHTSIZE,
         64))
        self.sr.buttonNav = uicls.Container(name='buttonPar', parent=self.sr.rightSide, align=uiconst.TOTOP, height=25, padRight=2)
        self.sr.finalizeBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=mls.UI_CHARCREA_FINALIZE, func=self.SaveWithStartLocation, left=10, args=(0,), state=uiconst.UI_HIDDEN, fixedwidth=70)
        self.sr.saveBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=mls.UI_CHARCREA_FINALIZE, func=self.Save, left=10, args=(), state=uiconst.UI_HIDDEN, fixedwidth=70)
        self.sr.approveBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=mls.UI_CMD_NEXT, func=self.Approve, left=10, args=(), fixedwidth=70)
        self.sr.backBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=mls.UI_GENERIC_BACK, func=self.Back, args=(), left=10, fixedwidth=70)
        self.sr.blackOut = uicls.Fill(parent=self, color=(0.0, 0.0, 0.0, 0.0))
        self.sr.mainCont = uicls.Container(name='mainCont', parent=self, align=uiconst.TOALL)
        self.sr.helpButton = uicls.Container(parent=self.sr.uiContainer, pos=(13, 19, 26, 26), state=uiconst.UI_HIDDEN, align=uiconst.BOTTOMLEFT, hint=mls.UI_SHARED_GETHELP, idx=0)
        helpIcon = uicls.Icon(parent=self.sr.helpButton, icon=ccConst.ICON_HELP, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
        self.sr.helpButton.OnClick = self.SetStepHelpText
        self.sr.helpButton.OnMouseEnter = (self.OnHelpMouseEnter, self.sr.helpButton)
        self.sr.helpButton.OnMouseExit = (self.OnHelpMouseExit, self.sr.helpButton)
        self.sr.helpButton.sr.icon = helpIcon
        self.sr.helpBox = uicls.Container(name='helpBox', parent=self.sr.uiContainer, pos=(0, 200, 350, 200), state=uiconst.UI_HIDDEN, align=uiconst.CENTER)
        self.sr.helpText = uicls.Label(text='', parent=self.sr.helpBox, align=uiconst.TOPLEFT, width=self.sr.helpBox.width)
        self.sr.helpFill = uicls.Fill(name='fill', parent=self.sr.helpBox, color=(0.0, 0.0, 0.0, 0.5), padding=(-8, -8, -8, -8), state=uiconst.UI_NORMAL)
        self.sr.helpFill.OnClick = self.SetStepHelpText
        self.avatarScene = None
        self.UpdateLayout()
        sm.RegisterNotify(self)



    def OnHelpMouseEnter(self, btn, *args):
        btn.sr.icon.SetAlpha(1.0)



    def OnHelpMouseExit(self, btn, *args):
        if not self.showingHelp:
            btn.sr.icon.SetAlpha(0.5)



    def ShowHelpText(self):
        self.showingHelp = 1
        self.sr.helpBox.state = uiconst.UI_NORMAL
        self.sr.helpBox.height = self.sr.helpText.textheight + 16
        self.sr.helpButton.sr.icon.SetAlpha(1.0)



    def HideHelpText(self):
        self.showingHelp = 0
        self.sr.helpText.text = ''
        self.sr.helpBox.state = uiconst.UI_HIDDEN
        self.sr.helpButton.sr.icon.SetAlpha(0.5)



    def SetStepHelpText(self, *args):
        postfix = ''
        if self.mode in [ccConst.MODE_LIMITED_RECUSTOMIZATION]:
            postfix = '_LIMITED'
        if not self.showingHelp and self.stepID in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP, ccConst.NAMINGSTEP):
            text = 'UI_CHARCREA_HELPTEXT_%d%s' % (self.stepID, postfix)
            self.sr.helpText.text = getattr(mls, text)
            self.ShowHelpText()
        else:
            self.HideHelpText()



    def SetHintText(self, modifier, hintText = ''):
        if self.stepID in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            self.sr.step.SetHintText(modifier, hintText)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetCharDetails(self, charID = None, gender = None, bloodlineID = None, dollState = None):
        self.ClearFacePortrait()
        self.dollState = dollState
        if charID:
            self.availableSteps = [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP]
            self.bloodlineID = bloodlineID
            self.genderID = int(gender)
            self.charID = charID
            self.dna = None
            dollData = sm.GetService('cc').GetPaperDollData(self.charID)
            if dollData is not None and dollState != const.paperdollStateForceRecustomize:
                self.dna = dollData
            bloodlineInfo = sm.GetService('cc').GetBloodlineDataByID().get(self.bloodlineID, None)
            if bloodlineInfo is None:
                raise UserError('CCNoBloodlineInfo')
            self.raceID = bloodlineInfo.raceID
            if dollState == const.paperdollStateFullRecustomizing:
                self.mode = ccConst.MODE_FULL_BLOODLINECHANGE
                self.availableSteps = [ccConst.RACESTEP,
                 ccConst.BLOODLINESTEP,
                 ccConst.CUSTOMIZATIONSTEP,
                 ccConst.PORTRAITSTEP,
                 ccConst.NAMINGSTEP]
            elif dollState in (const.paperdollStateResculpting, const.paperdollStateNoExistingCustomization, const.paperdollStateForceRecustomize):
                self.mode = ccConst.MODE_FULL_RECUSTOMIZATION
                self.availableSteps = [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP]
            self.mode = ccConst.MODE_LIMITED_RECUSTOMIZATION
            self.availableSteps = [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP]
        else:
            self.availableSteps = [ccConst.RACESTEP,
             ccConst.BLOODLINESTEP,
             ccConst.CUSTOMIZATIONSTEP,
             ccConst.PORTRAITSTEP,
             ccConst.NAMINGSTEP]
            self.charID = 0
            self.dna = None
            self.mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        stepID = self.availableSteps[0]
        self.stepsUsed = set([stepID])
        self.sr.mainCont.Flush()
        if self.sr.mainNav:
            self.sr.mainNav.Close()
        self.sr.mainNav = uicls.CharCreationNavigation(name='navigation', align=uiconst.CENTERTOP, parent=self.sr.leftSide, pos=(0, 16, 0, 60), stepID=stepID, func=self.SwitchStep, stepsUsed=self.stepsUsed, availableSteps=self.availableSteps)
        self.SwitchStep(stepID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetInfo(self):
        return uiutil.Bunch(charID=self.charID, raceID=self.raceID, bloodlineID=self.bloodlineID, genderID=self.genderID, dna=self.dna, ancestryID=self.ancestryID, schoolID=self.schoolID, stepID=self.stepID, charFirstName=self.charFirstName, charLastName=self.charLastName)



    def CanChangeBaseAppearance(self, *args):
        return self.mode in [ccConst.MODE_FULL_RECUSTOMIZATION, ccConst.MODE_FULLINITIAL_CUSTOMIZATION]



    def GetMode(self, *args):
        return self.mode



    def CanChangeBloodline(self, *args):
        return self.mode in [ccConst.MODE_FULL_BLOODLINECHANGE, ccConst.MODE_FULLINITIAL_CUSTOMIZATION]



    def CanChangeGender(self, *args):
        return self.mode not in [ccConst.MODE_FULL_BLOODLINECHANGE]



    def CanChangeName(self, *args):
        return self.mode in [ccConst.MODE_FULLINITIAL_CUSTOMIZATION]



    @bluepy.CCP_STATS_ZONE_METHOD
    def SwitchStep(self, toStep, *args):
        self.HideHelpText()
        if toStep == ccConst.RACESTEP:
            sm.StartService('audio').SendUIEvent(unicode('wise:/music_switch_full'))
        else:
            sm.StartService('audio').SendUIEvent(unicode('wise:/music_switch_ambient'))
        info = self.GetInfo()
        characters = self.characterSvc.characters
        if info.charID in characters and self.characterSvc.GetSingleCharactersDoll(info.charID).busyUpdating:
            raise UserError('uiwarning01')
        if toStep > self.stepID:
            passed = self.PassedStepCheck(toStep)
            if not passed:
                return 
        if self.stepID in [ccConst.CUSTOMIZATIONSTEP]:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_stop'))
            self.sr.step.StoreHistorySliderPosition()
        elif self.stepID == ccConst.PORTRAITSTEP:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_stop'))
            self.StorePortraitCameraSettings()
        self.LockEverything()
        self.sr.step = None
        uthread.new(self.sr.mainNav.PerformStepChange, toStep, self.stepsUsed)
        self.FadeToBlack(why=mls.UI_GENERIC_LOADING)
        if toStep == self.availableSteps[-1]:
            self.sr.approveBtn.state = uiconst.UI_HIDDEN
            if not self.charID:
                self.sr.finalizeBtn.state = uiconst.UI_NORMAL
                self.sr.saveBtn.state = uiconst.UI_HIDDEN
            else:
                self.sr.finalizeBtn.state = uiconst.UI_HIDDEN
            self.sr.saveBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.approveBtn.state = uiconst.UI_NORMAL
            self.sr.finalizeBtn.state = uiconst.UI_HIDDEN
            self.sr.saveBtn.state = uiconst.UI_HIDDEN
        self.sr.backBtn.state = uiconst.UI_NORMAL
        self.sr.mainCont.Flush()
        self.Cleanup()
        if toStep == ccConst.RACESTEP:
            self.StartRaceStep()
        elif toStep == ccConst.BLOODLINESTEP:
            self.StartBloodlineStep()
        elif toStep == ccConst.CUSTOMIZATIONSTEP:
            self.StartCustomizationStep()
        elif toStep == ccConst.PORTRAITSTEP:
            self.StartPortraitStep()
        elif toStep == ccConst.NAMINGSTEP:
            self.StartNamingStep()
        else:
            raise NotImplementedError
        if toStep in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP, ccConst.NAMINGSTEP):
            self.sr.helpButton.state = uiconst.UI_NORMAL
        else:
            self.sr.helpButton.state = uiconst.UI_HIDDEN
        self.stepID = toStep
        self.stepsUsed.add(toStep)
        self.UpdateBackdrop()
        self.UnlockEverything()
        self.setupDone = 1
        self.FadeFromBlack()



    @bluepy.CCP_STATS_ZONE_METHOD
    def StorePortraitCameraSettings(self):
        if self.camera is not None:
            self.storedPortraitCameraSettings = {'poi': self.camera.poi,
             'pitch': self.camera.pitch,
             'yaw': self.camera.yaw,
             'distance': self.camera.distance,
             'xFactor': self.camera.xFactor,
             'yFactor': self.camera.yFactor}



    @bluepy.CCP_STATS_ZONE_METHOD
    def FadeToBlack(self, why = ''):
        self.ShowLoading(why=why, forceOn=True)
        uicore.effect.CombineEffects(self.sr.blackOut, alpha=1.0, time=500.0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def FadeFromBlack(self):
        uthread.new(uicore.effect.CombineEffects, self.sr.blackOut, alpha=0.0, time=500.0)
        self.HideLoading(forceOff=1)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PassedStepCheck(self, toStep, *args):
        if not (max(self.stepsUsed) >= toStep or max(self.stepsUsed) + 1 == toStep):
            raise UserError('CCStepUnavailable')
        if toStep not in self.availableSteps:
            raise UserError('CCStepUnavailable')
        if toStep == ccConst.BLOODLINESTEP and self.raceID is None:
            raise UserError('CCMustSelectRace')
        if toStep == ccConst.CUSTOMIZATIONSTEP and (self.raceID is None or self.bloodlineID is None or self.genderID is None):
            raise UserError('CCMustSelectRaceAndBloodline')
        if toStep in [ccConst.PORTRAITSTEP, ccConst.NAMINGSTEP] and not prefs.GetValue('ignoreCCValidation', False):
            info = self.GetInfo()
            self.ToggleClothes(forcedValue=0)
            self.characterSvc.ValidateDollCustomizationComplete(info.charID)
        currentStepID = None
        if self.sr.step:
            currentStepID = self.sr.step.stepID
        if toStep == ccConst.NAMINGSTEP and currentStepID != ccConst.PORTRAITSTEP and self.GetActivePortrait() is None:
            raise UserError('CCStepUnavailable')
        if self.sr.step:
            self.sr.step.ValidateStepComplete()
        return True



    @bluepy.CCP_STATS_ZONE_METHOD
    def Approve(self, *args):
        idx = self.availableSteps.index(self.stepID)
        if len(self.availableSteps) > idx + 1:
            nextStep = self.availableSteps[(idx + 1)]
            self.SwitchStep(nextStep)
            uicore.registry.SetFocus(self)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SaveWithStartLocation(self, startInSpace, *args):
        settings.user.ui.Set('doTutorialDungeon', startInSpace)
        self.Save()



    @bluepy.CCP_STATS_ZONE_METHOD
    def Save(self, *args):
        try:
            self.LockEverything()
            if self.sr.step:
                self.sr.step.ValidateStepComplete()
            confirmed = self.AskForPortraitConfirmation()
            if not confirmed:
                return 
            if self.stepID != self.availableSteps[-1]:
                raise UserError('CCCannotSave')
            elif self.charID and self.mode in [ccConst.MODE_FULL_RECUSTOMIZATION, ccConst.MODE_LIMITED_RECUSTOMIZATION, ccConst.MODE_FULL_BLOODLINECHANGE]:
                self.UpdateExistingCharacter()
            elif self.bloodlineID is None or self.genderID is None:
                raise UserError('CCCannotSave2')
            else:
                isAvailable = self.sr.step.CheckAvailability()
                if isAvailable.charName is None:
                    eve.Message('CustomInfo', {'info': isAvailable.reason})
                    return 
                charID = self.SaveCurrentCharacter(isAvailable.charName, self.bloodlineID, self.genderID, self.activePortraitIndex)
                if charID:
                    self.characterSvc.CachePortraitInfo(charID, self.portraitInfo[self.activePortraitIndex])
                    try:
                        settings.user.ui.Set('doTutorialDungeon%s' % charID, 0)
                        settings.user.ui.Set('doIntroTutorial%s' % charID, 1)
                        sm.GetService('loading').ProgressWnd(mls.UI_CHARCREA_CHARACTERCREATION, mls.UI_CHARSEL_ENTERGAMEAS % {'name': cfg.eveowners.Get(charID).name}, 1, 2)
                        sm.GetService('loading').FadeToBlack(4000)
                        sm.GetService('sessionMgr').PerformSessionChange('charcreation', sm.RemoteSvc('charUnboundMgr').SelectCharacterID, charID, False, None)
                    except:
                        sm.GetService('loading').ProgressWnd(mls.UI_CHARSEL_CHARACTERSELECTION, mls.UI_CHARSEL_FAILED, 2, 2)
                        sm.GetService('loading').FadeFromBlack()
                        uthread.pool('GameUI :: GoCharacterSelection', sm.GetService('gameui').GoCharacterSelection, 1)
                        raise 

        finally:
            if self and not self.destroyed:
                self.UnlockEverything()




    @bluepy.CCP_STATS_ZONE_METHOD
    def Back(self, *args):
        idx = self.availableSteps.index(self.stepID)
        if idx == 0:
            if self.mode in [ccConst.MODE_FULLINITIAL_CUSTOMIZATION]:
                msg = 'AskCancelCharCreation'
            else:
                msg = 'AskCancelCharCustomization'
            if eve.Message(msg, {}, uiconst.YESNO) != uiconst.ID_YES:
                return 
            if self.mode != ccConst.MODE_FULLINITIAL_CUSTOMIZATION and self.dollState is None:
                self.ExitToStation(updateDoll=False)
            elif self.mode == ccConst.MODE_FULL_RECUSTOMIZATION and self.dollState not in DOLLSTATES_TO_RETURN_TO_CC:
                self.ExitToStation(updateDoll=False)
            else:
                sm.StartService('cc').GoBack()
        else:
            nextStep = self.availableSteps[(idx - 1)]
            self.SwitchStep(nextStep)
            uicore.registry.SetFocus(self)



    @bluepy.CCP_STATS_ZONE_METHOD
    def LockEverything(self, *args):
        if not getattr(self, 'setupDone', 0):
            return 
        self.state = uiconst.UI_DISABLED
        self.LockNavigation()



    @bluepy.CCP_STATS_ZONE_METHOD
    def LockNavigation(self, *args):
        if not getattr(self, 'setupDone', 0):
            return 
        self.sr.buttonNav.state = uiconst.UI_DISABLED
        self.sr.mainNav.state = uiconst.UI_DISABLED



    @bluepy.CCP_STATS_ZONE_METHOD
    def UnlockEverything(self, *args):
        self.state = uiconst.UI_PICKCHILDREN
        self.UnlockNavigation()



    @bluepy.CCP_STATS_ZONE_METHOD
    def UnlockNavigation(self, *args):
        if not self.isopen:
            return 
        self.sr.buttonNav.state = uiconst.UI_PICKCHILDREN
        if self.sr.mainNav:
            self.sr.mainNav.state = uiconst.UI_PICKCHILDREN



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetActivePortrait(self, portraitNo, *args):
        self.activePortraitIndex = portraitNo
        self.activePortrait = self.facePortraits[portraitNo]



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetActivePortrait(self):
        return self.activePortrait



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetFacePortrait(self, photo, portraitNo, *args):
        self.facePortraits[portraitNo] = photo
        self.SetActivePortrait(portraitNo)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearFacePortrait(self, *args):
        self.facePortraits = [None] * ccConst.NUM_PORTRAITS
        self.ClearPortraitInfo()
        self.activePortraitIndex = 0
        self.activePortrait = None



    @bluepy.CCP_STATS_ZONE_METHOD
    def SelectRace(self, raceID, check = 1):
        if self.raceID != raceID:
            oldRaceID = self.raceID
            if check and oldRaceID is not None and ccConst.BLOODLINESTEP in self.stepsUsed:
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    dnaLog = self.GetDollDNAHistory()
                    if dnaLog and len(dnaLog) > 1:
                        if eve.Message('CharCreationLoseChangesRace', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return 
            self.ClearSteps(what='race')
            self.ResetClothesStorage()
            self.raceID = raceID
            self.SelectBloodline(None, check=check)
            if hasattr(self.sr.step, 'OnRaceSelected'):
                self.sr.step.OnRaceSelected(raceID)
            self.UpdateBackdrop()



    @bluepy.CCP_STATS_ZONE_METHOD
    def SelectBloodline(self, bloodlineID, check = 1):
        if self.bloodlineID != bloodlineID:
            oldBloodlineID = self.bloodlineID
            if check and oldBloodlineID is not None and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed:
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    dnaLog = self.GetDollDNAHistory()
                    if dnaLog and len(dnaLog) > 1:
                        if eve.Message('CharCreationLoseChangeBloodline', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return 
            self.ClearSteps(what='bloodline')
            self.ResetClothesStorage()
            self.bloodlineID = bloodlineID
            if hasattr(self.sr.step, 'OnBloodlineSelected'):
                self.sr.step.OnBloodlineSelected(bloodlineID, oldBloodlineID)
            if self.bloodlineSelector is not None:
                self.bloodlineSelector.SelectBloodline(bloodlineID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SelectGender(self, genderID, check = 1):
        if not self.CanChangeGender():
            return 
        if check and self.genderID not in [None, genderID] and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed:
            if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                dnaLog = self.GetDollDNAHistory()
                if dnaLog and len(dnaLog) > 1:
                    if eve.Message('CharCreationLoseChangeGender', {}, uiconst.YESNO) != uiconst.ID_YES:
                        return 
        self.genderID = genderID
        self.ClearSteps(what='gender')
        self.ResetClothesStorage()
        if hasattr(self.sr.step, 'OnGenderSelected'):
            self.sr.step.OnGenderSelected(genderID)
        if getattr(self.sr.step.sr, 'historySlider'):
            self.sr.step.sr.historySlider.LoadHistory(0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SelectAncestry(self, ancestryID):
        self.ancestryID = ancestryID
        if hasattr(self.sr.step, 'OnAncestrySelected'):
            self.sr.step.OnAncestrySelected(ancestryID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SelectSchool(self, schoolID):
        self.schoolID = schoolID
        if hasattr(self.sr.step, 'OnSchoolSelected'):
            self.sr.step.OnSchoolSelected(schoolID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnDollUpdated(self, charID, redundantUpdate, fromWhere, *args):
        if fromWhere in ('AddCharacter', 'OnSetDevice'):
            return 
        self.ClearSteps(what='dollUpdated')



    @bluepy.CCP_STATS_ZONE_METHOD
    def IsSlowMachine(self):
        if prefs.GetValue('fastCharacterCreation', False):
            return True
        if prefs.GetValue('shaderQuality', 3) <= 2:
            return True
        return False



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        if 'fastCharacterCreation' in changes:
            if eve.Message('CustomQuestion', {'header': mls.UI_SHARED_LOSE_CHANGES,
             'question': mls.UI_CHARCREATION_LOSE_CHANGES}, uiconst.YESNO) == uiconst.ID_YES:
                self.avatarScene = None
                self.SwitchStep(self.availableSteps[0])
            else:
                prefs.fastCharacterCreation = 0
        elif self.stepID == ccConst.BLOODLINESTEP:
            self.SwitchStep(self.stepID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def TearDown(self):
        self.Cleanup()
        self.characterSvc.TearDown()
        if paperDoll.SkinSpotLightShadows.instance is not None:
            paperDoll.SkinSpotLightShadows.instance.Clear(killThread=True)
            paperDoll.SkinSpotLightShadows.instance = None
        self.floor = None
        self.doll = None
        self.scene = None
        self.avatarScene = None
        self.ClearCamera()
        if self.cameraUpdateJob and self.cameraUpdateJob in trinity.device.scheduledRecurring:
            trinity.device.scheduledRecurring.remove(self.cameraUpdateJob)
        self.cameraUpdateJob = None
        if self.bloodlineSelector is not None:
            self.bloodlineSelector.TearDown()
        self.bloodlineSelector = None



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartRaceStep(self):
        if not sm.GetService('cc').GetCharactersToSelect():
            self.sr.backBtn.state = uiconst.UI_HIDDEN
        sm.StartService('audio').SendUIEvent(unicode('wise:/music_switch_full'))
        uicore.layer.charactercreation.UpdateRaceMusic(self.raceID)
        self.sr.step = uicls.RaceStep(parent=self.sr.mainCont)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.Show2DBackdropScene()
        self.SetupScene(ccConst.SCENE_PATH_RACE_SELECTION)
        self.camera = cameras.CharCreationCamera(None)
        self.camera.fieldOfView = 0.5
        self.camera.distance = 7.0
        self.camera.SetPointOfInterest((0.0, 1.3, 0.0))
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.SetupCameraUpdateJob()
        self.camera.ToggleMode(ccConst.CAMERA_MODE_DEFAULT, avatar=None)
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartBloodlineStep(self):
        self.sr.step = uicls.CharacterBloodlineSelection(parent=self.sr.mainCont)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.Show2DBackdropScene()
        self.SetupScene(ccConst.SCENE_PATH_RACE_SELECTION)
        self.bloodlineSelector = ccUtil.BloodlineSelector(self.scene)
        if self.raceID and self.bloodlineSelector:
            self.bloodlineSelector.LoadRace(self.raceID, callBack=self.sr.step.MakeUI)
        self.camera = cameras.CharCreationCamera(None)
        self.camera.fieldOfView = 0.5
        self.camera.distance = 7.0
        self.camera.SetPointOfInterest((0.0, 1.3, 0.0))
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.CorrectBloodlinePlacement()
        self.SetupCameraUpdateJob()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        info = self.GetInfo()
        if info.bloodlineID is not None:
            self.bloodlineSelector.SelectBloodline(info.bloodlineID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CorrectBloodlinePlacement(self):
        aspect = trinity.device.viewport.GetAspectRatio()
        newDistance = 9.31 / aspect
        newDistance = max(7.0, newDistance)
        self.camera.distance = newDistance
        newHeight = 1.729 / aspect
        newHeight = max(1.3, newHeight)
        self.camera.SetPointOfInterest((0, newHeight, 0))



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetAvatarScene(self):
        info = self.GetInfo()
        if self.avatarScene is None:
            self.SetupScene(ccConst.SCENE_PATH_CUSTOMIZATION)
            self.avatarScene = self.scene
            self.AddCharacter(info.charID, info.bloodlineID, info.genderID, dna=info.dna)
            self.floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            self.scene.dynamics.append(self.floor)
        else:
            self.scene = self.avatarScene
        sceneManager = sm.GetService('sceneManager')
        sceneManager.SetActiveScenes(None, self.scene, sceneKey='characterCreation')



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartCustomizationStep(self, *args):
        info = self.GetInfo()
        self.UpdateRaceMusic(info.raceID)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.Show2DBackdropScene()
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 1)
            self.camera = cameras.CharCreationCamera(avatar, ccConst.CAMERA_MODE_FACE)
            self.camera.frontClip = 0.1
            self.camera.backclip = 100.0
            self.SetupCameraUpdateJob()
            self.camera.SetMoveCallback(self.CameraMoveCB)
        self.SetDefaultLighting()
        self.sr.step = uicls.CharacterCustomization(parent=self.sr.mainCont)
        if self.CanChangeBaseAppearance():
            self.StartEditMode(showPreview=True, callback=self.sr.step.ChangeSculptingCursor)
        self.camera.ToggleMode(ccConst.CAMERA_MODE_FACE, avatar=avatar, transformTime=500.0)
        if not sm.StartService('device').SupportsSM3():
            self.RemoveBodyModifications()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)



    def CameraMoveCB(self, viewMatrix):
        info = self.GetInfo()
        if info.charID not in self.characterSvc.characters:
            return 
        if not len(self.characterSvc.characters):
            return 
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        matrix = geo2.MatrixInverse(viewMatrix.transform)
        view = matrix[3][:3]
        joint = avatar.GetBoneIndex('Head')
        if joint == 4294967295L:
            return 
        head = avatar.GetBonePosition(joint)
        rot = avatar.rotation
        vec = (view[0] - head[0], view[1] - head[1], view[2] - head[2])
        vecLength = geo2.Vec3Distance((0, 0, 0), vec)
        vec = geo2.QuaternionTransformVector(geo2.QuaternionInverse(rot), vec)
        norm = 1.0 / math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])
        vec = (vec[0] * norm, vec[1] * norm, vec[2] * norm)
        leftright = math.atan2(vec[2], vec[0])
        updown = math.asin(vec[1])
        leftright = 1 - abs(leftright) / 3.1415927 * 2
        updown = 2 * updown / 3.1415927
        dist = (vecLength - 1.0) / 7.0
        network = avatar.animationUpdater.network
        network.SetControlParameter('ControlParameters|HeadLookLeftRight', leftright)
        network.SetControlParameter('ControlParameters|HeadLookUpDown', updown)
        network.SetControlParameter('ControlParameters|CameraDistance', dist)



    @bluepy.CCP_STATS_ZONE_METHOD
    def FetchOldPortraitData(self, charID):
        PREFIX = 'ControlParameters|'
        cache = self.characterSvc.GetCachedPortraitInfo(charID)
        if cache is not None:
            self.lightingID = cache.lightID
            self.lightColorID = cache.lightColorID
            self.lightIntensity = cache.lightIntensity
            path = self.GetBackgroundPathFromID(cache.backgroundID)
            if path in ccConst.backgroundOptions:
                self.backdropPath = path
            self.poseID = cache.poseData['PortraitPoseNumber']
            self.cameraPos = cache.cameraPosition
            self.cameraPoi = cache.cameraPoi
            params = []
            for key in cache.poseData:
                params.append((PREFIX + key, cache.poseData[key]))

            if len(params):
                self.characterSvc.SetControlParametersFromList(params, charID)
        else:
            portraitData = sm.GetService('cc').GetPortraitData(charID)
            if portraitData is not None:
                self.lightingID = portraitData.lightID
                self.lightColorID = portraitData.lightColorID
                self.lightIntensity = portraitData.lightIntensity
                path = self.GetBackgroundPathFromID(portraitData.backgroundID)
                if path in ccConst.backgroundOptions:
                    self.backdropPath = path
                self.poseID = portraitData.portraitPoseNumber
                FPP = paperDollUtil.FACIAL_POSE_PARAMETERS
                self.cameraPos = (portraitData.cameraX, portraitData.cameraY, portraitData.cameraZ)
                self.cameraPoi = (portraitData.cameraPoiX, portraitData.cameraPoiY, portraitData.cameraPoiZ)
                params = [[PREFIX + FPP.PortraitPoseNumber, portraitData['portraitPoseNumber']],
                 [PREFIX + FPP.HeadLookTarget, (portraitData['headLookTargetX'], portraitData['headLookTargetY'], portraitData['headLookTargetZ'])],
                 [PREFIX + FPP.HeadTilt, portraitData['headTilt']],
                 [PREFIX + FPP.OrientChar, portraitData['orientChar']],
                 [PREFIX + FPP.BrowLeftCurl, portraitData['browLeftCurl']],
                 [PREFIX + FPP.BrowLeftTighten, portraitData['browLeftTighten']],
                 [PREFIX + FPP.BrowLeftUpDown, portraitData['browLeftUpDown']],
                 [PREFIX + FPP.BrowRightCurl, portraitData['browRightCurl']],
                 [PREFIX + FPP.BrowRightTighten, portraitData['browRightTighten']],
                 [PREFIX + FPP.BrowRightUpDown, portraitData['browRightUpDown']],
                 [PREFIX + FPP.EyeClose, portraitData['eyeClose']],
                 [PREFIX + FPP.EyesLookVertical, portraitData['eyesLookVertical']],
                 [PREFIX + FPP.EyesLookHorizontal, portraitData['eyesLookHorizontal']],
                 [PREFIX + FPP.SquintLeft, portraitData['squintLeft']],
                 [PREFIX + FPP.SquintRight, portraitData['squintRight']],
                 [PREFIX + FPP.JawSideways, portraitData['jawSideways']],
                 [PREFIX + FPP.JawUp, portraitData['jawUp']],
                 [PREFIX + FPP.PuckerLips, portraitData['puckerLips']],
                 [PREFIX + FPP.FrownLeft, portraitData['frownLeft']],
                 [PREFIX + FPP.FrownRight, portraitData['frownRight']],
                 [PREFIX + FPP.SmileLeft, portraitData['smileLeft']],
                 [PREFIX + FPP.SmileRight, portraitData['smileRight']]]
                self.characterSvc.SetControlParametersFromList(params, charID)
        self.alreadyLoadedOldPortraitData = True



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartPortraitStep(self):
        info = self.GetInfo()
        if not getattr(self, 'alreadyLoadedOldPortraitData', False):
            if self.mode in [ccConst.MODE_FULL_RECUSTOMIZATION, ccConst.MODE_LIMITED_RECUSTOMIZATION]:
                self.FetchOldPortraitData(info.charID)
        self.sr.step = uicls.CharacterPortrait(parent=self.sr.mainCont)
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None and avatar.animationUpdater is not None:
            avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 2)
        if self.camera is None:
            self.camera = cameras.CharCreationCamera(avatar, ccConst.CAMERA_MODE_PORTRAIT)
            self.SetupCameraUpdateJob()
        else:
            self.camera.ToggleMode(ccConst.CAMERA_MODE_PORTRAIT, avatar=avatar, transformTime=500.0)
        if hasattr(self, 'cameraPos'):
            self.camera.PlacePortraitCamera(self.cameraPos, self.cameraPoi)
        if hasattr(self, 'storedPortraitCameraSettings'):
            self.camera.SetPointOfInterest(self.storedPortraitCameraSettings['poi'])
            self.camera.pitch = self.storedPortraitCameraSettings['pitch']
            self.camera.yaw = self.storedPortraitCameraSettings['yaw']
            self.camera.distance = self.storedPortraitCameraSettings['distance']
            self.camera.xFactor = self.storedPortraitCameraSettings['xFactor']
            self.camera.yFactor = self.storedPortraitCameraSettings['yFactor']
        self.UpdateLights()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        self.characterSvc.StartPosing(charID=info.charID, callback=self.sr.step.ChangeSculptingCursor)



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartNamingStep(self, *args):
        self.sr.step = uicls.CharacterNaming(parent=self.sr.mainCont)
        info = self.GetInfo()
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            if info.charID in self.characterSvc.characters:
                avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 1)
        self.camera = cameras.CharCreationCamera(avatar=avatar)
        self.camera.fieldOfView = 0.3
        self.camera.distance = 8.0
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.SetupCameraUpdateJob()
        self.camera.SetPointOfInterest((0.0, self.camera.avatarEyeHeight / 2.0, 0.0))
        self.SetDefaultLighting()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearSteps(self, what = None, force = 0, *args):
        stepAlreadyCleared = getattr(self.sr.step, 'stepAlreadyCleared', 0)
        if not force and stepAlreadyCleared or not getattr(self.sr.mainNav, 'ResetToStep', None):
            return 
        currentStepID = self.stepID
        if currentStepID <= ccConst.NAMINGSTEP:
            pass
        if currentStepID <= ccConst.PORTRAITSTEP:
            pass
        if currentStepID <= ccConst.CUSTOMIZATIONSTEP:
            self.ClearFacePortrait()
            self.ClearPortraitInfo()
            self.schoolID = None
            self.ancestryID = None
            if what in ('bloodline', 'race'):
                self.ancestryID = None
                self.schoolID = None
        if currentStepID <= ccConst.BLOODLINESTEP:
            self.avatarScene = None
            self.characterSvc.TearDown()
            self.ancestryID = None
            self.schoolID = None
        if currentStepID <= ccConst.RACESTEP:
            self.TearDown()
        self.stepsUsed = set(range(1, currentStepID)) or set([self.availableSteps[0]])
        self.sr.mainNav.ResetToStep(currentStepID, stepsUsed=self.stepsUsed)
        if self.sr.step:
            self.sr.step.stepAlreadyCleared = 1



    @bluepy.CCP_STATS_ZONE_METHOD
    def Cleanup(self):
        self.characterSvc.StopEditing()
        info = self.GetInfo()
        charID = info.charID
        if charID in self.characterSvc.characters:
            self.characterSvc.StopPosing(charID)
        self.bloodlineSelector = None
        self.scene = None
        self.ClearCamera()
        sceneManager = sm.GetService('sceneManager')
        sceneManager.UnregisterScene('characterCreation')
        sceneManager.UnregisterScene2('characterCreation')



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetupScene(self, path):
        scene1 = None
        scene2 = trinity.Load(path)
        blue.resMan.Wait()
        if self.IsSlowMachine():
            if hasattr(scene2, 'shadowCubeMap'):
                scene2.shadowCubeMap.enabled = False
            if hasattr(scene2, 'ssao') and hasattr(scene2.ssao, 'enable'):
                scene2.ssao.enable = False
            if hasattr(scene2, 'ambientColor'):
                scene2.ambientColor = (0.25, 0.25, 0.25)
            if hasattr(scene2, 'cells'):
                for cell in scene2.cells:
                    if hasattr(cell, 'subCells'):
                        for subcell in cell.subCells:
                            if hasattr(subcell, 'updateRadiosity'):
                                subcell.updateRadiosity = False
                            if hasattr(subcell, 'updateInputLighting'):
                                subcell.updateInputLighting = False
                            if hasattr(subcell, 'computeSphericalHarmonics'):
                                subcell.computeSphericalHarmonics = False


        elif scene2:
            if hasattr(scene2, 'shadowCubeMap'):
                scene2.shadowCubeMap.enabled = False
        self.scene = scene2
        if hasattr(trinity, 'Tr2PhysXScene'):
            trinityPhysXScene = trinity.Tr2PhysXScene()
            trinityPhysXScene.CreatePlane((0, 0, 0), (0, 1, 0), 0)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.RegisterScenes('characterCreation', scene1, scene2)
        sceneManager.SetRegisteredScenes('characterCreation')



    @bluepy.CCP_STATS_ZONE_METHOD
    def ReduceLights(self):
        scene = self.scene
        if hasattr(scene, 'lights'):
            lightsToRemove = []
            for each in scene.lights:
                if each.name != 'FrontMain':
                    lightsToRemove.append(each)

            for each in lightsToRemove:
                scene.lights.remove(each)

            if len(scene.lights) > 0:
                if hasattr(scene.lights[0], 'color'):
                    scene.lights[0].color = (0.886, 0.98, 1.0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def AddCharacter(self, charID, bloodlineID, genderID, scene = None, dna = None, validateColors = True):
        self.ResetDna()
        self.characterSvc.AddCharacterToScene(charID, scene or self.scene, ccUtil.GenderIDToPaperDollGender(genderID), dna=dna, bloodlineID=bloodlineID, updateDoll=False)
        self.doll = self.characterSvc.GetSingleCharactersDoll(charID)
        while self.doll.IsBusyUpdating():
            blue.synchro.Yield()

        self.doll.overrideLod = paperDoll.LOD_SKIN
        self.doll.useCachedRenderTargets = True
        textureQuality = prefs.GetValue('charTextureQuality', sm.GetService('device').GetDefaultCharTextureQuality())
        self.doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
        if self.IsSlowMachine():
            self.doll.useFastShader = True
        else:
            self.doll.useFastShader = False
        self.characterSvc.SetDollBloodline(charID, bloodlineID)
        if validateColors:
            for categoryName in ccConst.COLORMAPPING.keys() + [ccConst.skintone]:
                self.UpdateColorSelectionFromDoll(categoryName)
                self.ValidateColors(categoryName)

        if self.mode != ccConst.MODE_LIMITED_RECUSTOMIZATION:
            metadata = self.characterSvc.GetSingleCharactersMetadata(charID)
            typesInUse = metadata.types
            modifiersToRemove = []
            for (modifierName, resourceID,) in typesInUse.iteritems():
                if resourceID:
                    info = cfg.paperdollResources.Get(resourceID)
                    if info.typeID is not None:
                        modifiersToRemove.append(modifierName)

            for modifierName in modifiersToRemove:
                uicore.layer.charactercreation.ClearCategory(modifierName, doUpdate=False)

        self.StartDnaLogging()
        self.characterSvc.UpdateDoll(charID, fromWhere='AddCharacter')



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAvailableStyles(self, modifier):
        info = self.GetInfo()
        gender = info.genderID
        bloodline = info.bloodlineID
        currentModifier = self.characterSvc.GetModifierByCategory(info.charID, modifier)
        itemTypes = self.characterSvc.GetAvailableTypesByCategory(modifier, gender, bloodline)
        activeIndex = None
        if currentModifier:
            currentType = currentModifier.GetTypeData()
            for (i, each,) in enumerate(itemTypes):
                if each[1][0] == currentType[0] and each[1][1] == currentType[1]:
                    activeIndex = i

        return (itemTypes, activeIndex)



    def GetSkinToneColors(self, colors):
        retColors = []
        if colors is None:
            return []
        if type(colors) == types.TupleType and len(colors) != 0:
            if type(colors[0]) == types.TupleType:
                bloodline = colors[0][0]
            else:
                bloodline = colors[0]
        else:
            return []
        bloodline = bloodline.split('_')[0]
        baseColor = ccUtil.LoadFromYaml(SKINTONE_BASE_COLOR_PATH + bloodline + '.base')
        for (name, color,) in colors:
            displayColor = geo2.Vector(0.0, 0.0, 0.0, 1.0)
            if color and type(color[0]) == types.TupleType:
                for each in color:
                    displayColor = displayColor + each

                displayColor = displayColor / len(color)
                displayColor = 0.3 * displayColor + geo2.Vec4Scale(baseColor, 0.7)
                displayColor = geo2.Add(displayColor, (0.05, -0.05, -0.05, 0.0))
                displayColor = geo2.Vector(*displayColor)
            else:
                displayColor = color
            displayColor.w = 1.0
            displayColor = tuple(displayColor)
            retColors.append((name, displayColor, color))

        return retColors



    def GetModifierIntensity(self, modifierPath):
        info = self.GetInfo()
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, modifierPath)
        if modifier:
            return modifier[0].weight
        return 0.0



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetAvailableColors(self, modifier):
        info = self.GetInfo()
        (colors, activeColorIndex,) = self.characterSvc.GetCharacterColorVariations(info.charID, modifier)
        colors = tuple(colors)
        retColors = []
        if modifier == ccConst.skintone:
            retColors = self.GetSkinToneColors(colors)
        else:
            for (name, color,) in colors:
                if color and type(color[0]) == types.TupleType:
                    r = g = b = 0
                    for (_r, _g, _b, _a,) in color:
                        r += _r
                        g += _g
                        b += _b

                    r = r / float(len(color))
                    g = g / float(len(color))
                    b = b / float(len(color))
                    retColors.append((name, (r,
                      g,
                      b,
                      1.0), color))
                else:
                    retColors.append((name, color, color))

        return (retColors, activeColorIndex)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetColorValue(self, modifier, primaryColor, secondaryColor = None, doUpdate = True, ignoreValidate = False):
        self._setColorsByCategory[modifier] = (primaryColor, secondaryColor)
        info = self.GetInfo()
        self.characterSvc.SetColorValueByCategory(info.charID, modifier, primaryColor, secondaryColor, doUpdate=False)
        if ccUtil.HasUserDefinedSpecularity(modifier):
            specValue = self._setSpecularityByCategory.setdefault(modifier, 0.5)
            self.SetColorSpecularity(modifier, specValue, doUpdate=False)
        if ccUtil.HasUserDefinedWeight(modifier):
            defaultIntensity = ccConst.defaultIntensity.get(modifier, 0.5)
            intensityValue = self._setIntensityByCategory.setdefault(modifier, defaultIntensity)
            self.SetIntensity(modifier, intensityValue, doUpdate=False)
        if not ignoreValidate:
            self.ValidateColors(modifier)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetColorValue')



    def GetSpecularityByCategory(self, category):
        return self._setSpecularityByCategory.get(category, 0.5)



    def GetIntensityByCategory(self, category):
        return self._setIntensityByCategory.get(category, 0.5)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetRandomColorSpecularity(self, modifier, doUpdate = True):
        self.SetColorSpecularity(modifier, random.random(), doUpdate=doUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetColorSpecularity(self, modifier, specularity, doUpdate = True):
        self._setSpecularityByCategory[modifier] = specularity
        info = self.GetInfo()
        self.characterSvc.SetColorSpecularityByCategory(info.charID, modifier, specularity, doUpdate=doUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetRandomHairDarkness(self, doUpdate = True):
        self.SetHairDarkness(random.random(), doUpdate=doUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetHairDarkness(self, darkness, doUpdate = True):
        info = self.GetInfo()
        self.characterSvc.SetHairDarkness(info.charID, darkness)
        if doUpdate:
            sm.GetService('character').UpdateDoll(info.charID, fromWhere='SetHairDarkness')



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetRandomIntensity(self, modifier, doUpdate = True):
        self.SetIntensity(modifier, random.random(), doUpdate=doUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetIntensity(self, modifier, value, doUpdate = True):
        info = self.GetInfo()
        if modifier == ccConst.muscle:
            self.characterSvc.SetCharacterMuscularity(info.charID, value, doUpdate=doUpdate)
        elif modifier == ccConst.weight:
            self.characterSvc.SetCharacterWeight(info.charID, value, doUpdate=doUpdate)
        else:
            self._setIntensityByCategory[modifier] = value
            self.characterSvc.SetWeightByCategory(info.charID, modifier, value, doUpdate=doUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetItemType(self, itemType, weight = 1.0, doUpdate = True):
        info = self.GetInfo()
        category = self.characterSvc.GetCategoryFromResPath(itemType[1][0])
        if category in (ccConst.topouter,
         ccConst.topmiddle,
         ccConst.bottomouter,
         ccConst.outer,
         ccConst.feet,
         ccConst.glasses):
            for (mcat, modifier,) in self.clothesStorage.iteritems():
                if mcat == category:
                    break
            else:
                modifier = None

            if modifier:
                self.clothesStorage.pop(category)
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyTypeToDoll(info.charID, itemType, weight=weight, doUpdate=False)
        if category in self._setColorsByCategory:
            (var1, var2,) = self._setColorsByCategory[category]
            self.SetColorValue(category, var1, var2, doUpdate=False)
        self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetItemType')



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetStyle(self, category, style, variation = None, doUpdate = True):
        info = self.GetInfo()
        if style or variation or category in (ccConst.topouter,
         ccConst.topmiddle,
         ccConst.bottomouter,
         ccConst.outer,
         ccConst.feet,
         ccConst.glasses):
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyItemToDoll(info.charID, category, style, removeFirst=True, variation=variation, doUpdate=False)
        if style:
            if category in self._setColorsByCategory:
                (var1, var2,) = self._setColorsByCategory[category]
                self.SetColorValue(category, var1, var2, doUpdate=False)
            self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetStyle')



    @bluepy.CCP_STATS_ZONE_METHOD
    def ValidateColors(self, category):
        if category not in ccConst.COLORMAPPING:
            return 
        info = self.GetInfo()
        categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.bloodlineID)
        if not categoryColors:
            return 
        (primary, secondary,) = categoryColors
        hasValidColor = False
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
        if modifier:
            currentColor = modifier[0].GetColorizeData()
            if secondary:
                if modifier[0].metaData.numColorAreas > 1:
                    for primaryColorTuple in primary:
                        (primaryColorName, primaryDisplayColor, primaryColorValue,) = primaryColorTuple
                        (pA, pB, pC,) = primaryColorValue['colors']
                        for secondaryColorTuple in secondary:
                            (secondaryColorName, secondaryDisplayColor, secondaryColorValue,) = secondaryColorTuple
                            (srA, srB, srC,) = secondaryColorValue['colors']
                            if pA == currentColor[0] and srB == currentColor[1] and srC == currentColor[2]:
                                hasValidColor = True
                                if category not in self._setColorsByCategory or self._setColorsByCategory[category][1] == None:
                                    self.SetColorValue(category, primaryColorTuple, secondaryColorTuple, doUpdate=False, ignoreValidate=True)
                                break

                        if hasValidColor:
                            break

                    if not hasValidColor:
                        for primaryColorTuple in primary:
                            (primaryColorName, primaryDisplayColor, primaryColorValue,) = primaryColorTuple
                            if primaryColorValue['colors'] == currentColor:
                                hasValidColor = True
                                self.SetColorValue(category, primaryColorTuple, secondary[0], doUpdate=False, ignoreValidate=True)
                                break

                else:
                    for primaryColorTuple in primary:
                        (primaryColorName, primaryDisplayColor, primaryColorValue,) = primaryColorTuple
                        if primaryColorValue['colors'] == currentColor:
                            hasValidColor = True
                            if category not in self._setColorsByCategory:
                                self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                            break
                    else:
                        if category in self._setColorsByCategory:
                            hasValidColor = True

            else:
                for primaryColorTuple in primary:
                    (primaryColorName, primaryDisplayColor, primaryColorValue,) = primaryColorTuple
                    if primaryColorValue['colors'] == currentColor:
                        hasValidColor = True
                        if category not in self._setColorsByCategory:
                            self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                        break

            if not hasValidColor and primary:
                if secondary:
                    var2 = secondary[0]
                else:
                    var2 = None
                self.SetColorValue(category, primary[0], var2, doUpdate=False, ignoreValidate=True)



    def UpdateColorSelectionFromDoll(self, category):
        if category not in ccConst.COLORMAPPING:
            return 
        info = self.GetInfo()
        categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.bloodlineID)
        if not categoryColors:
            return 
        (primary, secondary,) = categoryColors
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
        if modifier:
            corPrimary = None
            corSecondary = None
            try:
                (chosenPrimary, chosenSecondary,) = self.characterSvc.GetSingleCharactersMetadata(info.charID).typeColors[category]
                for primaryColorTuple in primary:
                    if primaryColorTuple[0] == chosenPrimary:
                        corPrimary = primaryColorTuple
                        break

                if secondary and chosenSecondary:
                    for secondaryColorTuple in secondary:
                        if secondaryColorTuple[0] == chosenSecondary:
                            corSecondary = secondaryColorTuple
                            break

            except KeyError:
                log.LogWarn('KeyError when getting Metadata for a single character in characterCreationLayer.UpdateColorSelectionFromDoll', info.charID, category)
            if corPrimary is not None:
                self._setColorsByCategory[category] = (corPrimary, corSecondary)
            if category in self.characterSvc.characterMetadata[info.charID].typeWeights:
                self._setIntensityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeWeights[category]
            if category in self.characterSvc.characterMetadata[info.charID].typeSpecularity:
                self._setSpecularityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeSpecularity[category]



    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearCategory(self, category, doUpdate = True):
        self.SetStyle(category, style=None, doUpdate=doUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def CheckDnaLog(self, trigger = None):
        if self.sr.step and self.sr.step.sr.historySlider:
            (currentIndex, maxIndex,) = self.sr.step.sr.historySlider.GetCurrentIndexAndMaxIndex()
            if currentIndex != maxIndex:
                self.ClearDnaLogFromIndex(currentIndex)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearCamera(self):
        if self.camera is not None:
            for (priority, behavior,) in self.camera.cameraBehaviors:
                behavior.camera = None

            del self.camera.cameraBehaviors[:]
            self.camera.avatar = None
            self.camera = None



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetDefaultLighting(self):
        self.SetLightScene('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal.red')
        if self.IsSlowMachine():
            self.ReduceLights()



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetupCameraUpdateJob(self):
        sceneManager = sm.GetService('sceneManager')
        sceneManager.view = self.camera.viewMatrix
        sceneManager.projection = self.camera.projectionMatrix
        sceneManager.CreateJob()
        if self.cameraUpdateJob is None:
            self.cameraUpdateJob = trinity.renderJob.CreateRenderJob('cameraUpdate')
            r = trinity.TriStepPythonCB()
            r.SetCallback(self.UpdateCamera)
            self.cameraUpdateJob.steps.append(r)
            self.cameraUpdateJob.ScheduleRecurring()



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateCamera(self):
        if self.camera is not None:
            self.camera.Update()



    @bluepy.CCP_STATS_ZONE_METHOD
    def PickObjectUV(self, pos):
        return self.scene.PickObjectUV(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PickObjectAndArea(self, pos):
        return self.scene.PickObjectAndArea(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PickObject(self, pos):
        return self.scene.PickObject(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SaveCurrentCharacter(self, charactername, bloodlineID, genderID, portraitID):
        total = 3
        sm.GetService('loading').ProgressWnd(mls.UI_LOAD_REGISTERING, mls.UI_LOAD_COMPILEPREFS, 1, total)
        try:
            try:
                if self.portraitInfo[portraitID] is None:
                    raise UserError('CharCreationNoPortrait')
                info = self.GetInfo()
                charInfo = self.characterSvc.GetCharacterAppearanceInfo(info.charID)
                charID = sm.GetService('cc').CreateCharacterWithDoll(charactername, bloodlineID, genderID, info.ancestryID, charInfo, self.portraitInfo[portraitID], info.schoolID)
                sm.GetService('loading').ProgressWnd(mls.UI_LOAD_REGISTERING, mls.UI_CHARSEL_INSERTRECORD, 2, total)
                sm.GetService('photo').AddPortrait(self.GetPortraitSnapshotPath(portraitID), charID)
                sm.GetService('loading').ProgressWnd(mls.UI_LOAD_REGISTERING, mls.UI_GENERIC_DONE, 3, total)
                return charID
            except UserError as what:
                if not what.msg.startswith('CharNameInvalid'):
                    eve.Message(*what.args)
                    return 
                errorMsg = cfg.GetMessage(*what.args).text
                errorMsg += '<br><br>%s' % mls.UI_CHARSEL_CREATECHARERROR1
                sm.GetService('loading').ProgressWnd(mls.UI_LOAD_REGISTERING, mls.UI_CHARSEL_FAILEDSOMEREASON, 3, total)

        finally:
            self.sessionSounds = []




    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateExistingCharacter(self, *args):
        portraitID = self.activePortraitIndex
        charID = self.charID
        if self.portraitInfo[portraitID] is None:
            raise UserError('CharCreationNoPortrait')
        dollExists = self.dna is not None
        dollInfo = self.characterSvc.GetCharacterAppearanceInfo(charID)
        availableTypeIDs = sm.GetService('cc').GetMyApparel()
        metadata = self.characterSvc.characterMetadata[charID]
        typesInUse = metadata.types
        for resourceID in typesInUse.itervalues():
            if resourceID:
                info = cfg.paperdollResources.Get(resourceID)
                if info.typeID is not None and info.typeID not in availableTypeIDs:
                    typeName = cfg.invtypes.Get(info.typeID).typeName
                    raise UserError('ItemNotAtStation', {'item': typeName})

        if self.mode == ccConst.MODE_FULL_RECUSTOMIZATION:
            sm.GetService('cc').UpdateExistingCharacterFull(charID, dollInfo, self.portraitInfo[portraitID], dollExists)
        elif self.mode == ccConst.MODE_LIMITED_RECUSTOMIZATION:
            sm.GetService('cc').UpdateExistingCharacterLimited(charID, dollInfo, self.portraitInfo[portraitID], dollExists)
        elif self.mode == ccConst.MODE_FULL_BLOODLINECHANGE:
            info = self.GetInfo()
            sm.GetService('cc').UpdateExistingCharacterBloodline(charID, dollInfo, self.portraitInfo[portraitID], dollExists, info.bloodlineID)
        sm.GetService('photo').AddPortrait(self.GetPortraitSnapshotPath(portraitID), charID)
        self.characterSvc.CachePortraitInfo(self.charID, self.portraitInfo[self.activePortraitIndex])
        if self.dollState != const.paperdollStateForceRecustomize:
            self.ExitToStation()
        else:
            uthread.pool('GameUI :: GoCharacterSelection', sm.GetService('gameui').GoCharacterSelection, 1)



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetBackdrop(self, backdropPath):
        self.backdropPath = backdropPath



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetPoseID(self, poseID):
        self.poseID = poseID



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetLightScene(self, lightPath, scene = None):
        scene = scene or self.scene
        lightScene = trinity.Load(lightPath)
        if scene:
            lightList = []
            for l in scene.lights:
                lightList.append(l)

            for l in lightList:
                scene.RemoveLightSource(l)

            for l in lightScene.lights:
                scene.AddLightSource(l)

            if paperDoll.SkinSpotLightShadows.instance is not None:
                paperDoll.SkinSpotLightShadows.instance.RefreshLights()



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetLights(self, lightID):
        self.lightingID = lightID
        self.UpdateLights()



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetLight(self):
        return self.lightingID



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetLightColor(self, lightID):
        self.lightColorID = lightID
        self.UpdateLights()



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetLightColor(self):
        return self.lightColorID



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetLightsAndColor(self, lightID, colorID):
        self.lightingID = lightID
        self.lightColorID = colorID
        self.UpdateLights()



    @bluepy.CCP_STATS_ZONE_METHOD
    def SetLightIntensity(self, intensity):
        self.lightIntensity = intensity
        self.UpdateLights()



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetLightIntensity(self):
        return self.lightIntensity



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateLights(self):
        lightsPath = cfg.graphics.Get(self.lightingID).graphicFile
        lightColorPath = cfg.graphics.Get(self.lightColorID).graphicFile
        lightScene = trinity.Load(lightsPath)
        lightColorScene = trinity.Load(lightColorPath)
        ccUtil.SetupLighting(self.scene, lightScene, lightColorScene, self.lightIntensity)
        if self.IsSlowMachine():
            self.ReduceLights()



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBackdrop(self):
        return self.backdropPath



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetPoseId(self):
        return getattr(self, 'poseID', 0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartEditMode(self, callback = None, **kwds):
        if callback is None and kwds.get('mode', None) == 'sculpt':
            callback = getattr(self.sr.step, 'ChangeSculptingCursor', None)
        info = self.GetInfo()
        self.characterSvc.StartEditMode(info.charID, self.scene, self.camera, callback=callback, **kwds)



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateBackdropLite(self, raceID, mouseEnter = False, *args):
        bdScene = sm.GetService('sceneManager').Get2DBackdropScene()
        if not bdScene:
            return 
        blue.resMan.SetUrgentResourceLoads(True)
        for each in bdScene.children:
            each.display = False
            if mouseEnter:
                if raceID:
                    if each.name == 'mouseoverSprite_%d' % raceID:
                        each.display = True
                else:
                    each.display = True
            elif each.name == 'backdropSprite':
                each.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/RACE_Background_%d.dds' % raceID
                each.display = True

        blue.resMan.SetUrgentResourceLoads(False)



    @bluepy.CCP_STATS_ZONE_METHOD
    def UpdateBackdrop(self, *args):
        bdScene = sm.GetService('sceneManager').Get2DBackdropScene()
        if not bdScene:
            return 
        bdScene.clearBackground = True
        for each in bdScene.children[:]:
            bdScene.children.remove(each)

        for each in bdScene.curveSets[:]:
            bdScene.curveSets.remove(each)

        size = min(uicore.desktop.height, uicore.desktop.width)
        margin = -200
        info = self.GetInfo()
        if self.stepID == ccConst.RACESTEP:
            bgSize = min(uicore.desktop.width, uicore.desktop.height) * 1.5
            backdropSprite = trinity.Tr2Sprite2d()
            backdropSprite.name = u'backdropSprite'
            backdropSprite.displayWidth = bgSize
            backdropSprite.displayHeight = bgSize
            backdropSprite.displayX = (uicore.desktop.width - bgSize) / 2
            backdropSprite.displayY = (uicore.desktop.height - bgSize) / 2
            backdropSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
            backdropSprite.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/RACE_Background_START_None.dds'
            backdropSprite.display = True
            bdScene.children.append(backdropSprite)
            for race in [const.raceAmarr,
             const.raceMinmatar,
             const.raceCaldari,
             const.raceGallente]:
                mouseoverSprite = trinity.Tr2Sprite2d()
                mouseoverSprite.name = u'mouseoverSprite_%d' % race
                mouseoverSprite.displayWidth = bgSize
                mouseoverSprite.displayHeight = bgSize
                mouseoverSprite.displayX = (uicore.desktop.width - bgSize) / 2
                mouseoverSprite.displayY = (uicore.desktop.height - bgSize) / 2
                mouseoverSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
                mouseoverSprite.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/RACE_Background_START_%d.dds' % race
                mouseoverSprite.display = False
                bdScene.children.append(mouseoverSprite)

            if info.raceID:
                self.UpdateBackdropLite(info.raceID)
        elif self.stepID == ccConst.BLOODLINESTEP:
            bgSize = max(uicore.desktop.width, uicore.desktop.height)
            backdropSprite = trinity.Tr2Sprite2d()
            backdropSprite.name = u'backdropSprite'
            backdropSprite.displayWidth = bgSize
            backdropSprite.displayHeight = bgSize
            backdropSprite.displayY = (uicore.desktop.height - bgSize) / 2
            backdropSprite.displayX = (uicore.desktop.width - bgSize) / 2
            backdropSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
            backdropSprite.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/Bloodline_Background_%d.dds' % info.raceID
            backdropSprite.display = True
            bdScene.children.append(backdropSprite)
        elif info.raceID == const.raceCaldari:
            rn = 'caldari'
            bgcolor = (74 / 255.0, 87 / 255.0, 97 / 255.0)
        elif info.raceID == const.raceAmarr:
            rn = 'amarr'
            bgcolor = (93 / 255.0, 89 / 255.0, 74 / 255.0)
        elif info.raceID == const.raceMinmatar:
            rn = 'minmatar'
            bgcolor = (92 / 255.0, 81 / 255.0, 80 / 255.0)
        elif info.raceID == const.raceGallente:
            rn = 'gallente'
            bgcolor = (77 / 255.0, 94 / 255.0, 93 / 255.0)
        else:
            rn = 'caldari'
            bgcolor = (74 / 255.0, 87 / 255.0, 97 / 255.0)
            log.LogWarn('Unknown raceID in characterCreationLayer.UpdateBackground', info.raceID)
        mainHalo = trinity.Tr2Sprite2d()
        mainHalo.name = u'mainHalo'
        mainHalo.texturePrimary = trinity.Tr2Sprite2dTexture()
        mainHalo.blendMode = trinity.TR2_SBM_ADD
        (r, g, b,) = bgcolor
        mainHalo.color = (r * 0.75,
         g * 0.75,
         b * 0.75,
         1.0)
        mainHalo.displayWidth = mainHalo.displayHeight = max(uicore.desktop.width, uicore.desktop.height) * 1.5
        mainHalo.displayX = (uicore.desktop.width - mainHalo.displayWidth) / 2
        mainHalo.displayY = (uicore.desktop.height - mainHalo.displayHeight) / 2
        mainHalo.display = True
        mainHalo.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/mainCenterHalo.dds'
        bdScene.children.append(mainHalo)
        if self.stepID == ccConst.PORTRAITSTEP:
            activeBackdrop = self.GetBackdrop()
            if activeBackdrop:
                portraitBackground = trinity.Tr2Sprite2d()
                portraitBackground.name = u'portraitBackground'
                bdScene.children.insert(0, portraitBackground)
                portraitBackground.displayX = (uicore.desktop.width - size) * 0.5
                portraitBackground.displayY = (uicore.desktop.height - size) * 0.5
                portraitBackground.displayWidth = size
                portraitBackground.displayHeight = size
                if not portraitBackground.texturePrimary:
                    portraitBackground.texturePrimary = trinity.Tr2Sprite2dTexture()
                    portraitBackground.texturePrimary.resPath = activeBackdrop
                portraitBackground.color = (1, 1, 1, 1)
                portraitBackground.display = True
                portraitBackground.blendMode = trinity.TR2_SBM_BLEND
        else:
            mainSize = size - margin
            cs = trinity.TriCurveSet()
            cs.name = 'RotationCurveSet'
            bdScene.curveSets.append(cs)
            for (textureNo, textureSize,) in ((1, 468 / 1024.0),
             (2, 580 / 1024.0),
             (3, 1.0),
             (4, 1.0)):
                tf = trinity.Tr2Sprite2dTransform()
                tf.name = u'tf'
                tf.displayX = uicore.desktop.width * 0.5
                tf.displayY = uicore.desktop.height * 0.5
                bdScene.children.append(tf)
                circleBG = trinity.Tr2Sprite2d()
                circleBG.name = u'circleBG'
                circleBG.texturePrimary = trinity.Tr2Sprite2dTexture()
                circleBG.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/circularRaceBgs/%s_%s.dds' % (rn, textureNo)
                circleBG.color = (0.025, 0.025, 0.025, 1.0)
                circleBG.blendMode = trinity.TR2_SBM_BLEND
                circleBG.displayWidth = mainSize * textureSize
                circleBG.displayHeight = mainSize * textureSize
                circleBG.displayX = -circleBG.displayWidth * 0.5
                circleBG.displayY = -circleBG.displayHeight * 0.5
                circleBG.display = True
                tf.children.append(circleBG)
                rotationCurve = self.CreatePerlinCurve(cs, scale=16.0, offset=10.0, speed=0.001, alpha=0.9, beta=1.0 + random.random())
                self.CreateBinding(cs, rotationCurve, tf, 'rotation', 'value')

            cs.Play()



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateBinding(self, curveSet, curve, destinationObject, attribute, sourceAttribute = 'currentValue'):
        binding = trinity.TriValueBinding()
        curveSet.bindings.append(binding)
        binding.destinationObject = destinationObject
        binding.destinationAttribute = attribute
        binding.sourceObject = curve
        binding.sourceAttribute = sourceAttribute
        return binding



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateScalarCurve(self, curveSet, length, endValue, startTimeOffset = 0.0, startValue = 0.0, cycle = False):
        curve = trinity.Tr2ScalarCurve()
        if startTimeOffset:
            curve.AddKey(0.0, startValue)
        curve.AddKey(startTimeOffset, startValue)
        curve.AddKey(startTimeOffset + length, endValue)
        curve.interpolation = trinity.TR2CURVE_HERMITE
        curve.cycle = cycle
        curveSet.curves.append(curve)
        return curve



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreatePerlinCurve(self, curveSet, scale = 1.0, offset = 6.0, speed = 1.1, alpha = 1.0, beta = 1.1):
        curve = trinity.TriPerlinCurve()
        curve.scale = scale
        curve.offset = offset
        curve.speed = speed
        curve.alpha = alpha
        curve.beta = beta
        curveSet.curves.append(curve)
        return curve



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetLightID(self):
        path = self.lightingID
        files = ccConst.LIGHT_SETTINGS_ID
        for (i, light,) in enumerate(files):
            if path == light:
                return i

        return 1



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetLightColorID(self):
        path = self.lightColorID
        files = ccConst.LIGHT_COLOR_SETTINGS_ID
        for (i, light,) in enumerate(files):
            if path == light:
                return i

        return 1



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBackgroundID(self):
        path = self.backdropPath
        ID = path.split('_')[-1].split('.')[0]
        ID = int(ID)
        return ID



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBackgroundPathFromID(self, bgID):
        return 'res:/UI/Texture/CharacterCreation/backdrops/Background_' + str(bgID) + '.dds'



    @bluepy.CCP_STATS_ZONE_METHOD
    def CapturePortrait(self, portraitID, *args):
        if self.camera is None:
            return 
        self.portraitInfo[portraitID] = util.KeyVal(cameraPosition=self.camera.GetPosition(), cameraFieldOfView=self.camera.fieldOfView, cameraPoi=self.camera.GetPointOfInterest(), backgroundID=self.GetBackgroundID(), lightID=self.lightingID, lightColorID=self.lightColorID, lightIntensity=self.GetLightIntensity(), poseData=self.characterSvc.GetPoseData())
        size = 512
        sceneManager = sm.GetService('sceneManager')
        scene = sceneManager.GetActiveScene2()
        backdropPath = self.backdropPath
        if backdropPath:
            backdropScene = trinity.Tr2Sprite2dScene()
            backdropScene.displayWidth = size
            backdropScene.displayHeight = size
            sprite = trinity.Tr2Sprite2d()
            sprite.texturePrimary = trinity.Tr2Sprite2dTexture()
            sprite.texturePrimary.resPath = backdropPath
            sprite.displayWidth = size
            sprite.displayHeight = size
            backdropScene.children.append(sprite)
        target = trinity.TriSurfaceManaged(trinity.device.CreateRenderTarget, size, size, trinity.TRIFMT_X8R8G8B8, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        depth = trinity.TriSurfaceManaged(trinity.device.CreateDepthStencilSurface, size, size, trinity.TRIFMT_D16, trinity.TRIMULTISAMPLE_NONE, 0, 1)
        surface = trinity.TriSurfaceManaged(trinity.device.CreateOffscreenPlainSurface, size, size, trinity.TRIFMT_X8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        renderJob = trinity.CreateRenderJob('TakeSnapShot')
        renderJob.SetRenderTarget(target)
        renderJob.SetDepthStencil(depth)
        projection = trinity.TriProjection()
        projection.PerspectiveFov(self.camera.fieldOfView, 1, 0.01, 200)
        view = self.camera.viewMatrix
        renderJob.Clear((0.0, 0.0, 0.0, 1.0), 1.0)
        renderJob.SetProjection(projection)
        renderJob.SetView(view)
        if backdropPath:
            renderJob.Update(backdropScene)
            renderJob.RenderScene(backdropScene)
        renderJob.RenderScene(scene)
        trinity.WaitForResourceLoads()
        renderJob.ScheduleOnce()
        renderJob.WaitForFinish()
        trinity.device.GetRenderTargetData(target, surface)
        filename = self.GetPortraitSnapshotPath(portraitID)
        surface.SaveSurfaceToFile(filename, trinity.TRIIFF_JPG)
        path = 'cache:/Pictures/Portraits/PortraitSnapshot_%s_%s.jpg' % (portraitID, session.userid)
        blue.resMan.ClearCachedObject(path)
        tex = blue.resMan.GetResource(path, 'atlas')
        return tex



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetPortraitSnapshotPath(self, portraitID):
        return blue.os.cachepath + '/Pictures/Portraits/PortraitSnapshot_%s_%s.jpg' % (portraitID, session.userid)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearPortraitInfo(self):
        self.portraitInfo = [None] * ccConst.NUM_PORTRAITS



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetPortraitInfo(self, portraitID):
        return self.portraitInfo[portraitID]



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetDNA(self, getHiddenModifiers = False, getWeightless = False):
        return self.doll.GetDNA(getHiddenModifiers=getHiddenModifiers, getWeightless=getWeightless)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetRandomLastName(self, bloodlineID):
        try:
            return random.choice(cfg.bloodlineNames[bloodlineID])['lastName']
        except KeyError:
            self.characterSvc.LogError('Bloodline with ID', bloodlineID, 'has no last names defined!')
            return ''



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnHideUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_HIDDEN



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnShowUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_PICKCHILDREN



    def OnMapShortcut(self, *args):
        uicore.cmd.commandMap.UnloadAllAccelerators()
        uicore.cmd.commandMap.LoadAcceleratorsByCategory(mls.UI_GENERIC_GENERAL)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ShowLoading(self, why = '', top = 200, forceOn = 0, *args):
        wheel = self.sr.loadingWheel
        wheel.top = top
        wheel.hint = why
        wheel.forcedOn = forceOn
        wheel.Show()



    @bluepy.CCP_STATS_ZONE_METHOD
    def HideLoading(self, why = '', forceOff = 0, *args):
        wheel = self.sr.loadingWheel
        if not wheel.forcedOn or forceOff:
            self.sr.loadingWheel.Hide()
            wheel.forcedOn = 0



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnCloseView(self):
        uicore.cmd.LoadAllAccelerators()
        sm.GetService('tutorial').ChangeTutorialWndState(visible=True)
        self.TearDown()
        sm.GetService('audio').SendUIEvent(unicode('wise:/music_character_creation_stop'))
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_stop'))
        if self.jukeboxWasPlaying:
            sm.StartService('jukebox').Play()
        if sm.GetService('audio').GetWorldVolume() == 0.0:
            sm.GetService('audio').SetWorldVolume(self.worldLevel)
        sm.GetService('cc').ClearMyAvailabelTypeIDs()



    @bluepy.CCP_STATS_ZONE_METHOD
    def ExitToStation(self, updateDoll = True):
        dna = self.GetDNA()
        self.OnCloseView()
        if session.worldspaceid is not None:
            change = {'stationid': [None, session.stationid],
             'worldspaceid': [None, session.worldspaceid]}
            sm.GetService('gameui').OnSessionChanged(False, session, change)
            sm.GetService('entityClient').ProcessSessionChange(False, session, change)
            sm.GetService('navigation').OnSessionChanged(False, session, change)
            sm.GetService('graphicClient').OnSessionChanged(False, session, change)
            if updateDoll is True and prefs.GetValue('loadstationenv', 1):
                pdc = sm.GetService('entityClient').GetPlayerEntity(canBlock=True).components['paperdoll'].doll
                pdc.doll.buildDataManager = paperDoll.BuildDataManager()
                pdc.doll.LoadDNA(dna, pdc.factory)
                pdc.Update()
        else:
            change = {'stationid': (None, session.stationid)}
            sm.GetService('gameui').OnSessionChanged(isRemote=False, session=session, change=change)



    def ToggleClothes(self, forcedValue = None, doUpdate = True, *args):
        valueBefore = self.clothesOff
        if forcedValue is None:
            self.clothesOff = not self.clothesOff
        else:
            self.clothesOff = forcedValue
        if valueBefore == self.clothesOff:
            return 
        info = self.GetInfo()
        if info.charID in self.characterSvc.characters:
            character = self.characterSvc.GetSingleCharacter(info.charID)
            if self.clothesOff:
                self.RemoveClothes(character, doUpdate=doUpdate)
            else:
                self.ReApplyClothes(character, doUpdate=doUpdate)



    @bluepy.CCP_STATS_ZONE_METHOD
    def ReApplyClothes(self, character, doUpdate = True):
        if len(self.clothesStorage) == 0 or character is None:
            return 
        for (mcat, modifier,) in self.clothesStorage.iteritems():
            character.doll.buildDataManager.AddModifier(modifier)

        self.ResetClothesStorage()
        if doUpdate:
            sm.GetService('character').UpdateDollsAvatar(character)



    @bluepy.CCP_STATS_ZONE_METHOD
    def RemoveClothes(self, character, doUpdate = True):
        if len(self.clothesStorage) != 0 or character is None:
            return 
        categoriesToRemove = paperDoll.BODY_CATEGORIES - (paperDoll.BODY_CATEGORIES.SKIN,
         paperDoll.BODY_CATEGORIES.TATTOO,
         paperDoll.BODY_CATEGORIES.TOPUNDERWEAR,
         paperDoll.BODY_CATEGORIES.BOTTOMUNDERWEAR,
         paperDoll.BODY_CATEGORIES.TOPINNER,
         paperDoll.BODY_CATEGORIES.BOTTOMINNER,
         paperDoll.BODY_CATEGORIES.SKINTONE,
         paperDoll.BODY_CATEGORIES.SCARS)
        self.ResetClothesStorage()
        for category in categoriesToRemove:
            for modifier in character.doll.buildDataManager.GetModifiersByCategory(category):
                if modifier.respath not in paperDoll.DEFAULT_NUDE_PARTS:
                    self.clothesStorage[category] = modifier
                    character.doll.buildDataManager.RemoveModifier(modifier)


        modifier = self.characterSvc.GetModifierByCategory(self.charID, ccConst.glasses)
        if modifier:
            self.clothesStorage[ccConst.glasses] = modifier
            character.doll.buildDataManager.RemoveModifier(modifier)
        if doUpdate:
            sm.GetService('character').UpdateDollsAvatar(character)



    def ResetClothesStorage(self, *args):
        self.clothesStorage = {}



    def RemoveBodyModifications(self, *args):
        try:
            if getattr(self, 'bodyModRemoved', 0):
                return 
            modifiersToRemove = [ccConst.p_earslow,
             ccConst.p_earshigh,
             ccConst.p_nose,
             ccConst.p_nostril,
             ccConst.p_brow,
             ccConst.p_lips,
             ccConst.p_chin,
             ccConst.t_head,
             ccConst.s_head]
            character = self.characterSvc.GetSingleCharacter(self.charID)
            for mod in modifiersToRemove:
                modifiers = self.characterSvc.GetModifiersByCategory(self.charID, mod)
                for m in modifiers:
                    character.doll.buildDataManager.RemoveModifier(m)
                    self.characterSvc.RemoveFromCharacterMetadata(self.charID, mod)


            self.bodyModRemoved = 1
            sm.GetService('character').UpdateDollsAvatar(character)
        except Exception:
            pass



    @bluepy.CCP_STATS_ZONE_METHOD
    def StartDnaLogging(self):
        self.dnaList = []
        self.lastLitHistoryBit = None



    def ResetDna(self, *args):
        self.dnaList = None
        self.lastLitHistoryBit = None



    @bluepy.CCP_STATS_ZONE_METHOD
    def ClearDnaLogFromIndex(self, fromIndex):
        if self.dnaList:
            to = fromIndex + 1
            if to > len(self.dnaList):
                to = len(self.dnaList)
            self.dnaList = self.dnaList[:to]



    def AskForPortraitConfirmation(self, *args):
        photo = self.GetActivePortrait()
        wnd = sm.StartService('window').GetWindow('ccConfirmationWindow', create=1, decoClass=form.CCConfirmationWindow, photo=photo)
        if wnd.ShowModal() == uiconst.ID_YES:
            return True
        else:
            return False



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetDollDNAHistory(self):
        return self.dnaList



    def TryStoreDna(self, lastUpdateRedundant, fromWhere, sculpting = 0, force = 0, allowReduntant = 0, *args):
        if not lastUpdateRedundant or fromWhere in ('RandomizeCharacterGroups', 'RandomizeCharacter', 'AddCharacter'):
            if not self.isopen:
                return 
            if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                if self.sr.step is None:
                    return 
                if not force and self.sr.step.menuMode == self.sr.step.TATTOOMENU:
                    self.sr.step.tattooChangeMade = 1
                    return 
            if self.dnaList is not None:
                self.CheckDnaLog('UpdateDoll')
                dna = self.GetDNA(getHiddenModifiers=True, getWeightless=True)
                if not allowReduntant:
                    try:
                        (currentIndex, maxIndex,) = self.sr.step.sr.historySlider.GetCurrentIndexAndMaxIndex()
                        if dna == self.dnaList[currentIndex][0]:
                            return 
                    except Exception:
                        pass
                currMetadata = copy.deepcopy(self.characterSvc.characterMetadata[self.charID])
                self.dnaList.append((dna, currMetadata))
                if lastUpdateRedundant or force:
                    sm.ScatterEvent('OnHistoryUpdated')



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadDnaFromHistory(self, historyIndex):
        if len(self.characterSvc.characters) > 0:
            character = self.characterSvc.GetSingleCharacter(self.charID)
            if character:
                historyIndex = max(0, min(len(self.dnaList) - 1, historyIndex))
                (dna, metadata,) = self.dnaList[historyIndex]
                self.ToggleClothes(forcedValue=0, doUpdate=False)
                self.characterSvc.MatchDNA(character, dna)
                self.characterSvc.characterMetadata[self.charID] = metadata
                if self.characterSvc.GetSculptingActive():
                    sculpting = self.characterSvc.GetSculpting()
                    sculpting.UpdateFieldsBasedOnExistingValues(character.doll)
                self.characterSvc.UpdateDoll(self.charID, fromWhere='LoadDnaFromHistory', registerDna=False)
                self.characterSvc.SynchronizeHairColors(self.charID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PassMouseEventToSculpt(self, type, x, y):
        if not hasattr(self, 'characterSvc'):
            return 
        pickValue = None
        sculpting = self.characterSvc.GetSculpting()
        if sculpting and self.characterSvc.GetSculptingActive():
            if type == 'LeftDown':
                pickValue = sculpting.PickWrapper(x, y)
            elif type == 'LeftUp':
                pickValue = sculpting.EndMotion(x, y)
            elif type == 'Motion':
                pickValue = sculpting.MotionWrapper(x, y)
        return pickValue



    def UpdateRaceMusic(self, raceID = None):
        if not self.raceMusicStarted:
            bgMusic = sm.StartService('jukebox').GetState()
            if bgMusic == 'play':
                sm.StartService('jukebox').Pause()
                self.jukeboxWasPlaying = True
            sm.StartService('audio').SendUIEvent(unicode('wise:/music_character_creation_play'))
            self.raceMusicStarted = True
        racialMusicDict = {const.raceCaldari: 'wise:/music_switch_race_caldari',
         const.raceMinmatar: 'wise:/music_switch_race_minmatar',
         const.raceAmarr: 'wise:/music_switch_race_amarr',
         const.raceGallente: 'wise:/music_switch_race_gallente',
         None: 'music_switch_race_norace'}
        racialMusic = racialMusicDict.get(raceID, None)
        sm.StartService('audio').SendUIEvent(unicode(racialMusic))




class CharCreationNavigation(uicls.Container):
    __guid__ = 'uicls.CharCreationNavigation'
    default_align = uiconst.TOPLEFT
    default_height = 110
    default_state = uiconst.UI_NORMAL
    ANIMATIONTIME = 500.0
    MOUSEOVEROPACITY = 0.8
    NORMALOPACITY = 0.3
    ACTIVEOPACITY = 1.0
    NUMSTEPS = 5
    FONTSIZE = 16

    @bluepy.CCP_STATS_ZONE_METHOD
    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.stepID = attributes.stepID
        self.stepsUsed = attributes.stepsUsed
        self.availableSteps = attributes.availableSteps
        self.attributesApplied = 0
        self.callbackFunc = attributes.func
        self.sr.header = uicls.CCLabel(name='header', parent=self, align=uiconst.TOTOP, top=0, autowidth=0, width=300, uppercase=1, letterspace=2, color=(0.9, 0.9, 0.9, 0.8), fontsize=self.FONTSIZE, bold=False)
        width = self.NUMSTEPS * 36
        self.width = width
        self.sr.stepCont = uicls.Container(name='stepCont', parent=self, align=uiconst.CENTERTOP, pos=(0,
         26,
         width,
         26))
        self.CreateSteps()
        self.ResetToStep(self.stepID, set([self.availableSteps[0]]))



    @bluepy.CCP_STATS_ZONE_METHOD
    def CreateSteps(self, *args):
        self.sr.stepCont.Flush()
        left = 0
        circleFile = 'res:/UI/Texture/CharacterCreation/navigator/ring.dds'
        dotFile = 'res:/UI/Texture/CharacterCreation/navigator/dot.dds'
        for i in xrange(self.availableSteps[0], self.availableSteps[-1] + 1):
            if i not in self.availableSteps:
                continue
            step = uicls.Container(name='step%s' % i, parent=self.sr.stepCont, align=uiconst.TOPLEFT, pos=(left,
             0,
             36,
             36), state=uiconst.UI_DISABLED)
            step.tlCont = uicls.Container(name='tlCont', parent=step, align=uiconst.TOPLEFT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uicls.Sprite(name='tlSprite', parent=step.tlCont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            step.trCont = uicls.Container(name='trCont', parent=step, align=uiconst.TOPRIGHT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uicls.Sprite(name='trSprite', parent=step.trCont, align=uiconst.TOPRIGHT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            step.blCont = uicls.Container(name='blCont', parent=step, align=uiconst.BOTTOMLEFT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uicls.Sprite(name='blSprite', parent=step.blCont, align=uiconst.BOTTOMLEFT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            step.brCont = uicls.Container(name='trCont', parent=step, align=uiconst.BOTTOMRIGHT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uicls.Sprite(name='brSprite', parent=step.brCont, align=uiconst.BOTTOMRIGHT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            sprite = uicls.Sprite(name='step%s' % i, parent=step, align=uiconst.TOPLEFT, pos=(2, 2, 32, 32), state=uiconst.UI_DISABLED, texturePath=dotFile)
            step.SetOpacity(self.NORMALOPACITY)
            left += 36
            step.id = i
            step.OnMouseEnter = (self.OnStepMouseOver, step)
            step.OnMouseExit = (self.OnStepMouseExit, step)
            step.OnClick = (self.OnStepClicked, step)
            self.sr.Set('step%s' % i, step)

        self.sr.stepCont.width = left
        left = 20
        connectorFile = 'res:/UI/Texture/CharacterCreation/navigator/connector.dds'
        gradientFile = 'res:/UI/Texture/CharacterCreation/navigator/connector_fade.dds'
        for i in xrange(self.availableSteps[0] + 1, self.availableSteps[-1] + 1):
            if i - 1 not in self.availableSteps:
                continue
            cont = uicls.Container(name='space%s' % i, parent=self.sr.stepCont, align=uiconst.TOPLEFT, pos=(left,
             10,
             0,
             16), state=uiconst.UI_DISABLED, clipChildren=1)
            self.sr.Set('connector%s' % i, cont)
            sprite = uicls.Sprite(name='connector%s' % i, parent=cont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 16), state=uiconst.UI_DISABLED, texturePath=connectorFile)
            sprite.SetAlpha(self.NORMALOPACITY)
            sprite = uicls.Sprite(name='connector_fade%s' % i, parent=cont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 16), state=uiconst.UI_DISABLED, texturePath=gradientFile)
            self.sr.Set('connector_fade%s' % i, sprite)
            left += 36

        self.attributesApplied = 1



    @bluepy.CCP_STATS_ZONE_METHOD
    def ResetToStep(self, resetToStep, stepsUsed, *args):
        self.stepID = resetToStep
        self.stepsUsed = stepsUsed
        self.CreateSteps()
        firstCont = self.sr.Get('step%s' % self.availableSteps[0])
        firstCont.state = uiconst.UI_NORMAL
        self.OpenRight(firstCont, time=0.0)
        if max(stepsUsed) < 1:
            firstCont.SetOpacity(self.ACTIVEOPACITY)
            secondCont = self.sr.Get('step%s' % self.availableSteps[1])
            secondCont.state = uiconst.UI_NORMAL
            self.OpenLeft(secondCont, time=0.0)
        else:
            for stepID in xrange(self.availableSteps[0], resetToStep + 1):
                self.PerformStepChange(stepID, stepsUsed, forceOpen=1, time=0)

        self.stepsUsed.add(resetToStep)



    @bluepy.CCP_STATS_ZONE_METHOD
    def PerformStepChange(self, stepID, stepsUsed, forceOpen = 0, time = None):
        if not forceOpen:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_step_navigation_anim_play'))
        if not self.attributesApplied:
            return 
        if time is None:
            time = self.ANIMATIONTIME
        self.stepID = stepID
        self.stepsUsed = stepsUsed
        headerText = getattr(mls, 'UI_CHARCREA_STEP%s' % stepID, '')
        self.sr.header.text = '<center>%s' % headerText
        self.sr.header.SetAlpha(1.0)
        container = getattr(self.sr, 'step%s' % stepID, None)
        mousedStep = container.id
        stepsUsed = self.stepsUsed.copy()
        try:
            if (max(stepsUsed) >= mousedStep or max(stepsUsed) + 1 == mousedStep) and self.callbackFunc:
                for i in xrange(1, self.NUMSTEPS + 1):
                    connectorFade = getattr(self.sr, 'connector_fade%s' % i, None)
                    cont = getattr(self.sr, 'step%s' % i, None)
                    if connectorFade:
                        if i == mousedStep:
                            connectorFade.state = uiconst.UI_DISABLED
                        else:
                            connectorFade.state = uiconst.UI_HIDDEN
                    if cont and i != mousedStep:
                        cont.SetOpacity(self.NORMALOPACITY)

                cont = getattr(self.sr, 'step%s' % mousedStep, None)
                if mousedStep not in stepsUsed or forceOpen:
                    connector = self.sr.Get('connector%s' % mousedStep, None)
                    if connector:
                        if time:
                            uicore.effect.CombineEffects(connector, width=32, time=time)
                        else:
                            connector.width = 32
                        cont.SetOpacity(self.ACTIVEOPACITY)
                        if mousedStep not in [self.availableSteps[0], self.availableSteps[-1]]:
                            self.OpenRight(container, time=time)
                    nextStep = self.sr.Get('step%s' % str(mousedStep + 1), None)
                    if nextStep:
                        self.OpenLeft(nextStep, time=time)
                        nextStep.state = uiconst.UI_NORMAL
                if not container.dead and container.id == self.stepID:
                    container.SetOpacity(self.ACTIVEOPACITY)
        except AttributeError as e:
            if self is None or self.destroyed or e.message == 'SetOpacity':
                sm.GetService('cc').LogWarn('Attibute error ignored when performing step change')
            else:
                raise 



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnStepClicked(self, stepClicked, *args):
        if self.callbackFunc:
            if self.stepID == stepClicked.id:
                if not eve.session.role & service.ROLE_PROGRAMMER:
                    return 
            apply(self.callbackFunc, (stepClicked.id,))



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnStepMouseOver(self, container, *args):
        mousedStep = container.id
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))
        if mousedStep == self.stepID:
            return 
        if max(self.stepsUsed) >= mousedStep or max(self.stepsUsed) + 1 == mousedStep:
            container.SetOpacity(self.MOUSEOVEROPACITY)
        else:
            return 
        headerText = getattr(mls, 'UI_CHARCREA_STEP%s' % mousedStep, '')
        self.sr.header.text = '<center>%s' % headerText
        self.sr.header.SetAlpha(0.3)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OnStepMouseExit(self, container, *args):
        if container.id == self.stepID:
            container.SetOpacity(self.ACTIVEOPACITY)
            return 
        container.SetOpacity(self.NORMALOPACITY)
        headerText = getattr(mls, 'UI_CHARCREA_STEP%s' % self.stepID, '')
        self.sr.header.text = '<center>%s' % headerText
        self.sr.header.SetAlpha(1.0)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OpenLeft(self, container, time = 0.0, *args):
        tlCont = getattr(container, 'tlCont', None)
        blCont = getattr(container, 'blCont', None)
        if time == 0.0:
            tlCont.height = blCont.height = 10
            return 
        uthread.new(uicore.effect.CombineEffects, tlCont, height=10, time=time)
        uicore.effect.CombineEffects(blCont, height=10, time=time)



    @bluepy.CCP_STATS_ZONE_METHOD
    def OpenRight(self, container, time = 0.0, *args):
        trCont = getattr(container, 'trCont', None)
        brCont = getattr(container, 'brCont', None)
        if time == 0.0:
            trCont.height = brCont.height = 10
            return 
        uthread.new(uicore.effect.CombineEffects, trCont, height=10, time=time)
        uicore.effect.CombineEffects(brCont, height=10, time=time)




class CCConfirmationWindow(uicls.Window):
    __guid__ = 'form.CCConfirmationWindow'
    default_width = 540
    default_height = 326

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        photo = attributes.photo
        self.isModal = True
        self.SetTopparentHeight(0)
        self.sr.main.Flush()
        self.MakeUnResizeable()
        buttonContainer = uicls.Container(name='', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 30))
        self.sr.headerParent.state = uiconst.UI_HIDDEN
        self.width = self.default_width
        self.height = self.default_height
        top = 40
        btns = uicls.ButtonGroup(btns=[[mls.UI_CMD_OK, self.Confirm, ()], [mls.UI_CMD_CANCEL, self.Cancel, ()]], parent=buttonContainer, idx=0)
        self.sr.centerCont = uicls.Container(name='centerCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(20, 20, 20, 0))
        self.sr.leftSide = uicls.Container(name='leftSide', parent=self.sr.centerCont, align=uiconst.TOLEFT, pos=(0, 0, 260, 0))
        self.sr.portraitCont = uicls.Container(name='portraitCont', parent=self.sr.leftSide, align=uiconst.TOPLEFT, pos=(0, 0, 256, 256))
        uicls.Frame(parent=self.sr.portraitCont, color=(1.0, 1.0, 1.0, 1.0))
        self.sr.facePortrait = uicls.Icon(parent=self.sr.portraitCont, align=uiconst.TOALL)
        if photo is not None:
            self.sr.facePortrait.texture.atlasTexture = photo
            self.sr.facePortrait.texture.atlasTexture.Reload()
        self.sr.rightSide = uicls.Container(name='rightSide', parent=self.sr.centerCont, align=uiconst.TOALL, padding=(10, 0, 0, 0))
        caption = uicls.Label(text=mls.UI_CHARCREA_CONFIRMATIONHEADER, parent=self.sr.rightSide, align=uiconst.TOTOP, pos=(0, 0, 0, 50), fontsize=20, linespace=20, letterspace=1, idx=-1, state=uiconst.UI_DISABLED, uppercase=1, autowidth=0, autoheight=0, name='caption')
        text = uicls.Label(text=mls.UI_CHARCREA_CONFIRMATION, parent=self.sr.rightSide, align=uiconst.TOALL, autowidth=0, autoheight=0)



    def Confirm(self, *args):
        self.result = True
        self.SetModalResult(uiconst.ID_YES)



    def Cancel(self, *args):
        self.result = False
        self.SetModalResult(uiconst.ID_NO)




