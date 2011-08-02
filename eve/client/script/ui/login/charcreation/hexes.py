import uiconst
import uicls
import random
import uthread
import math
import uix
import util
import ccConst
import blue
import operator
FILL_MOUSEOVER = 0.1
FILL_SELECTION = 0.2
TEXT_MOUSEOVER = 0.6
TEXT_SELECTION = 1.0
TEXT_NORMAL = 0.8

class CCRacePicker(uicls.Container):
    __guid__ = 'uicls.CCRacePicker'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.isActive = 0
        self.raceInfo = attributes.raceInfo
        self.raceID = attributes.raceID
        self.selectedBloodlineID = None
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self._OnGlobalMouseUp)
        self.showText = attributes.showText
        self.bloodlineID = attributes.bloodlineID
        self.genderID = attributes.genderID
        self.PrepareInfo()
        self.clickable = attributes.get('clickable', 1)
        self.disabledHex = attributes.get('disabledHex', [])
        self.hexHeight = 64
        self.hexWidth = 64
        self.padding = -16
        self.padding2 = -int(math.sqrt(math.pow(self.padding, 2) + math.pow(0.5 * self.padding, 2))) - 2
        self.width = 200
        self.height = 206
        self.Setup()



    def Setup(self, *args):
        info = uicore.layer.charactercreation.GetInfo()
        self.sr.genderCont = uicls.Container(name='genderCont', parent=self, pos=(0,
         0,
         200,
         int(1.5 * self.hexHeight)), align=uiconst.TOPLEFT)
        self.sr.bloodlineCont = uicls.Container(name='bloodlineCont', parent=self, pos=(0,
         int(1.0 * self.hexHeight + 1.0 * self.padding),
         200,
         2 * self.hexHeight), align=uiconst.TOPLEFT)
        self.sr.raceBloodlineCont = uicls.Container(parent=self, pos=(0,
         int(2.0 * (self.hexHeight + self.padding)),
         200,
         2 * self.hexHeight), align=uiconst.TOPLEFT)
        self.CreateRaceHex()
        self.CreateBloodlineHex()
        self.CreateGenderHex()
        left = self.hexWidth + 20
        if self.showText:
            if info.raceID:
                raceTextCont = uicls.Container(name='raceTextCont', parent=self.sr.raceBloodlineCont, pos=(0,
                 int(0.5 * (self.padding + self.hexHeight)),
                 0,
                 self.hexHeight), align=uiconst.TOTOP)
                raceInfo = sm.GetService('cc').GetRaceDataByID()[info.raceID]
                raceName = Tr(raceInfo.raceName, 'character.races.raceName', raceInfo.dataID)
                text = '%s<br><b>%s</b>' % (mls.UI_CHARCREA_RACE, raceName)
                raceText = uicls.CCLabel(parent=raceTextCont, fontsize=12, align=uiconst.CENTERLEFT, text=text, letterspace=1, top=0, pos=(0, 0, 150, 0), autoheight=1, autowidth=0, left=left, bold=0, color=ccConst.COLOR50)
                if info.bloodlineID:
                    bloodline = sm.GetService('cc').GetBloodlineDataByID()[info.bloodlineID]
                    if bloodline and bloodline.raceID == info.raceID:
                        bloodlineTextCont = uicls.Container(name='bloodlineTextCont', parent=self.sr.bloodlineCont, text=text, pos=(0,
                         int(0.5 * (self.padding + self.hexHeight)),
                         0,
                         self.hexHeight), align=uiconst.TOTOP)
                        bloodlineName = Tr(bloodline.bloodlineName, 'character.bloodlines.bloodlineName', bloodline.dataID)
                        text = '%s<br><b>%s</b>' % (mls.UI_CHARCREA_BLOODLINE, bloodlineName)
                        bloodlineText = uicls.CCLabel(parent=bloodlineTextCont, fontsize=12, align=uiconst.CENTERLEFT, text=text, letterspace=1, autoheight=1, autowidth=1, left=left, bold=0, color=ccConst.COLOR50)
            if self.genderID is not None:
                genderText = [mls.UI_GENERIC_FEMALE, mls.UI_GENERIC_MALE][self.genderID]
                text = '%s<br><b>%s</b>' % (mls.UI_GENERIC_GENDER, genderText)
                genderTextCont = uicls.Container(name='genderTextCont', parent=self.sr.genderCont, text=text, pos=(0,
                 int(0.5 * (self.padding + self.hexHeight)),
                 0,
                 self.hexHeight), align=uiconst.TOTOP)
                genderText = uicls.CCLabel(parent=genderTextCont, fontsize=12, align=uiconst.CENTERLEFT, text=text, letterspace=1, autoheight=1, autowidth=1, left=left, bold=0, color=ccConst.COLOR50)



    def CreateRaceHex(self, *args):
        yOffset = int(0.5 * (self.padding + self.hexHeight))
        xOffset = int(self.hexWidth + self.padding2)
        offsetMap = {0: (0, yOffset),
         1: (xOffset, 0),
         2: (xOffset, self.padding + self.hexHeight),
         3: (2 * xOffset, yOffset)}
        self.AddRaceHex(offsetMap, self.hexWidth, self.hexHeight, self.currentRaceInfo, hexClassString='CCHexButtonRace2')
        self.ChangeStateOfAlmostAllConts(self.raceConts, uiconst.UI_HIDDEN, [self.raceID])
        self.SelectHex(self.raceConts.get(self.raceID), [])



    def SetText(self, *args):
        info = uicore.layer.charactercreation.GetInfo()
        text = ''
        if info.raceID:
            raceInfo = sm.GetService('cc').GetRaceDataByID()[info.raceID]
            raceName = Tr(raceInfo.raceName, 'character.races.raceName', raceInfo.dataID)
            text += '%s: %s' % (mls.UI_CHARCREA_RACE, raceName)
            if info.bloodlineID:
                bloodline = sm.GetService('cc').GetBloodlineDataByID()[info.bloodlineID]
                if bloodline and bloodline.raceID == info.raceID:
                    bloodlineName = Tr(bloodline.bloodlineName, 'character.bloodlines.bloodlineName', bloodline.dataID)
                    text += '     %s: %s' % (mls.UI_CHARCREA_BLOODLINE, bloodlineName)
        if info.genderID is not None:
            genderText = [mls.UI_GENERIC_FEMALE, mls.UI_GENERIC_MALE][info.genderID]
            text += '    %s: %s' % (mls.UI_GENERIC_GENDER, genderText)
        if hasattr(self, 'selectionText'):
            self.selectionText.text = text
        elif hasattr(self.parent, 'selectionText'):
            self.parent.selectionText.text = text



    def AddRaceHex(self, offsetMap, width, height, raceInfo, state = uiconst.UI_NORMAL, hexClassString = 'CCHexButtonRace2', *args):
        self.raceConts = {}
        isClickable = self.clickable and 'race' not in self.disabledHex
        for (i, race,) in enumerate(raceInfo):
            (left, top,) = offsetMap.get(i, (0, 0))
            hexClass = getattr(uicls, hexClassString)
            hex = hexClass(name='raceHex', parent=self.sr.raceBloodlineCont, align=uiconst.TOPLEFT, state=state, pos=(left,
             top,
             width,
             height), pickRadius=int(height / 2.0), info=race, id=race.raceID, hexName=Tr(race.raceName, 'character.races.raceName', race.dataID), func=self.OnRaceClicked, iconNum=int(math.log(race.raceID, 2)), clickable=isClickable)
            self.raceConts[race.raceID] = hex




    def CreateBloodlineHex(self, *args):
        yOffset = self.padding + self.hexHeight
        xOffset = int(self.hexWidth + self.padding2)
        offsetMap = {0: (0, int(0.5 * yOffset)),
         1: (xOffset, 0),
         2: (xOffset, yOffset)}
        self.AddBloodlineHex(offsetMap, self.hexWidth, self.hexHeight, self.currentBloodlineInfo)
        self.ChangeStateOfAlmostAllConts(self.bloodlineConts, uiconst.UI_HIDDEN, [self.bloodlineID])
        self.SelectHex(self.bloodlineConts.get(self.bloodlineID), [])



    def AddBloodlineHex(self, offsetMap, width, height, bloodlineInfo, state = uiconst.UI_NORMAL, hexClassString = 'CCHexButtonMedium', *args):
        self.bloodlineConts = {}
        hexClass = getattr(uicls, hexClassString)
        isClickable = self.clickable and 'bloodline' not in self.disabledHex
        for (i, bloodline,) in enumerate(bloodlineInfo):
            (left, top,) = offsetMap.get(i, (0, 0))
            hex = hexClass(name='bloodlineHex', parent=self.sr.bloodlineCont, align=uiconst.TOPLEFT, state=state, pos=(left,
             top,
             width,
             height), pickRadius=int(height / 2.0), info=bloodline, id=bloodline.bloodlineID, hexName=Tr(bloodline.bloodlineName, 'character.bloodlines.bloodlineName', bloodline.dataID), func=self.OnBloodlineClicked, iconNum=bloodline.bloodlineID - 1, clickable=isClickable)
            self.bloodlineConts[bloodline.bloodlineID] = hex




    def CreateGenderHex(self, *args):
        offsetMap = {0: (0, int(0.5 * (self.hexHeight + self.padding))),
         1: (self.hexWidth + self.padding2, 0)}
        self.AddGenderHex(offsetMap, self.hexWidth, self.hexHeight, self.currentGenderInfo, hexClassString='CCHexButtonGender2')
        self.ChangeStateOfAlmostAllConts(self.genderConts, uiconst.UI_HIDDEN, [self.genderID])
        self.SelectHex(self.genderConts.get(self.genderID), [])



    def AddGenderHex(self, offsetMap, width, height, genderInfo, state = uiconst.UI_NORMAL, hexClassString = 'CCHexButtonGender', *args):
        self.genderConts = {}
        hexClass = getattr(uicls, hexClassString)
        isClickable = self.clickable and 'gender' not in self.disabledHex
        for (i, info,) in enumerate(genderInfo):
            id = info.get('genderID', 0)
            gender = info.get('text', 0)
            (left, top,) = offsetMap.get(i, (0, 0))
            hex = hexClass(name='genderHex', parent=self.sr.genderCont, align=uiconst.TOPLEFT, state=state, pos=(left,
             top,
             width,
             height), pickRadius=int(height / 2.0), info=info, id=id, hexName=gender, func=self.OnGenderClicked, iconNum=id, clickable=isClickable)
            self.genderConts[id] = hex




    def OnHexMouseOver(self, cont, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))
        if getattr(cont, 'frame', None) is not None:
            cont.frame.state = uiconst.UI_DISABLED



    def OnHexMouseExit(self, cont, *args):
        if getattr(cont, 'frame', None) is not None:
            cont.frame.state = uiconst.UI_HIDDEN



    def _AnimateHexList(self, containerList, time = 100.0, attribute = 'left'):
        containerList.sort(key=operator.attrgetter(attribute))
        for cont in containerList:
            cont.state = uiconst.UI_NORMAL
            blue.pyos.synchro.Sleep(time)




    def SelectHex(self, cont, allConts):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
        for c in allConts:
            c.normalCont.state = uiconst.UI_DISABLED
            c.selection.state = uiconst.UI_HIDDEN

        self.SetSelectionState(cont, on=0)



    def PrepareInfo(self, *args):
        self.currentRaceInfo = sm.GetService('cc').GetRaceData()[:]
        self.RearrangeInfo(self.raceID, 'raceID', self.currentRaceInfo)
        self.currentBloodlineInfo = sm.GetService('cc').GetBloodlineDataByRaceID().get(self.raceID, [])[:]
        self.RearrangeInfo(self.bloodlineID, 'bloodlineID', self.currentBloodlineInfo)
        self.currentGenderInfo = [util.KeyVal(genderID=0, text=mls.UI_GENERIC_FEMALE), util.KeyVal(genderID=1, text=mls.UI_GENERIC_MALE)]
        self.RearrangeInfo(self.genderID, 'genderID', self.currentGenderInfo)



    def OnRaceClicked(self, cont, *args):
        info = uicore.layer.charactercreation.GetInfo()
        if not uicore.layer.charactercreation.CanChangeBloodline() or not self.clickable:
            return 
        newRaceID = cont.info.raceID
        self.ChangeStateOfAlmostAllConts(self.genderConts, uiconst.UI_HIDDEN, [self.genderID])
        self.ChangeStateOfAlmostAllConts(self.bloodlineConts, uiconst.UI_HIDDEN, [self.bloodlineID])
        if newRaceID == self.raceID:
            self.ClickingOnCurrent(self.raceID, cont, self.raceConts, what=['race'])
        else:
            dnaLog = uicore.layer.charactercreation.GetDollDNAHistory()
            if dnaLog and len(dnaLog) > 1:
                if eve.Message('CharCreationLoseChangesRace', {}, uiconst.YESNO) != uiconst.ID_YES:
                    return 
            self.isActive = 1
            self.Disable()
            self.raceID = newRaceID
            self.sr.raceBloodlineCont.Flush()
            self.RearrangeInfo(self.raceID, 'raceID', self.currentRaceInfo)
            self.CreateRaceHex()
            self.SelectHex(self.raceConts.get(self.raceID), [])
            uicore.layer.charactercreation.SelectRace(self.raceID, check=0)
            newBloodlineIdx = random.randint(0, 2)
            bloodlineInfoForRace = sm.GetService('cc').GetBloodlineDataByRaceID().get(newRaceID, [])
            bloodlineInfo = bloodlineInfoForRace[newBloodlineIdx]
            newBloodlineID = bloodlineInfo.bloodlineID
            self.currentBloodlineInfo = bloodlineInfoForRace
            self.RearrangeInfo(newBloodlineID, 'bloodlineID', self.currentBloodlineInfo)
            self.SwitchBloodline(newBloodlineID)
            self.Enable()



    def RearrangeInfo(self, id, what, info, *args):
        selectedIdx = None
        for (i, each,) in enumerate(info):
            if getattr(each, what, '') == id:
                selectedIdx = i
                break

        if selectedIdx is not None:
            currentPick = info[selectedIdx]
            oldPick = info[0]
            info[selectedIdx] = oldPick
            info[0] = currentPick



    def OnGenderClicked(self, cont, *args):
        info = uicore.layer.charactercreation.GetInfo()
        if info.charID or not self.clickable:
            return 
        newGenderID = cont.info.get('genderID', 0)
        self.ChangeStateOfAlmostAllConts(self.raceConts, uiconst.UI_HIDDEN, [self.raceID])
        self.ChangeStateOfAlmostAllConts(self.bloodlineConts, uiconst.UI_HIDDEN, [self.bloodlineID])
        if newGenderID == self.genderID:
            self.ClickingOnCurrent(self.genderID, cont, self.genderConts, what=['gender'])
        else:
            dnaLog = uicore.layer.charactercreation.GetDollDNAHistory()
            if dnaLog and len(dnaLog) > 1:
                if eve.Message('CharCreationLoseChangeGender', {}, uiconst.YESNO) != uiconst.ID_YES:
                    return 
            self.isActive = 1
            self.Disable()
            self.SwitchGender(newGenderID)
            self.Enable()



    def OnBloodlineClicked(self, cont, *args):
        info = uicore.layer.charactercreation.GetInfo()
        if not uicore.layer.charactercreation.CanChangeBloodline() or not self.clickable:
            return 
        newBloodlineID = cont.info.bloodlineID
        if newBloodlineID == self.bloodlineID:
            self.ClickingOnCurrent(self.bloodlineID, cont, self.bloodlineConts, what=['bloodline'])
            self.ChangeStateOfAlmostAllConts(self.genderConts, uiconst.UI_HIDDEN, [self.genderID])
            self.ChangeStateOfAlmostAllConts(self.raceConts, uiconst.UI_HIDDEN, [self.raceID])
        else:
            dnaLog = uicore.layer.charactercreation.GetDollDNAHistory()
            if dnaLog and len(dnaLog) > 1:
                if eve.Message('CharCreationLoseChangeBloodline', {}, uiconst.YESNO) != uiconst.ID_YES:
                    return 
            self.isActive = 1
            self.Disable()
            self.SwitchBloodline(newBloodlineID)
            self.Enable()



    def SwitchGender(self, newGenderID, *args):
        uicore.layer.charactercreation.FadeToBlack(why=mls.UI_GENERIC_LOADING)
        sm.GetService('character').StopEditing()
        self.genderID = newGenderID
        self.sr.genderCont.Flush()
        self.RearrangeInfo(self.genderID, 'genderID', self.currentGenderInfo)
        self.CreateGenderHex()
        self.SelectHex(self.genderConts.get(self.genderID), [])
        info = uicore.layer.charactercreation.GetInfo()
        sm.GetService('character').RemoveCharacter(info.charID)
        uicore.layer.charactercreation.AddCharacter(info.charID, info.bloodlineID, newGenderID)
        uicore.layer.charactercreation.SelectGender(self.genderID, check=0)
        uicore.layer.charactercreation.StartEditMode(mode='sculpt', resetAll=True)
        if hasattr(uicore.layer.charactercreation.sr.step, 'LoadFaceMode'):
            uthread.new(uicore.layer.charactercreation.sr.step.LoadFaceMode)
        uicore.layer.charactercreation.FadeFromBlack()



    def SwitchBloodline(self, newBloodlineID, *args):
        uicore.layer.charactercreation.FadeToBlack(why=mls.UI_GENERIC_LOADING)
        sm.GetService('character').StopEditing()
        self.bloodlineID = newBloodlineID
        self.sr.bloodlineCont.Flush()
        self.RearrangeInfo(self.bloodlineID, 'bloodlineID', self.currentBloodlineInfo)
        self.CreateBloodlineHex()
        self.SelectHex(self.bloodlineConts.get(self.bloodlineID), [])
        info = uicore.layer.charactercreation.GetInfo()
        sm.GetService('character').RemoveCharacter(info.charID)
        uicore.layer.charactercreation.AddCharacter(info.charID, newBloodlineID, info.genderID)
        uicore.layer.charactercreation.SelectBloodline(self.bloodlineID, check=0)
        doll = sm.GetService('character').GetSingleCharactersDoll(info.charID)
        while doll.busyUpdating:
            blue.synchro.Yield()

        uicore.layer.charactercreation.StartEditMode(mode='sculpt', resetAll=True)
        step = uicore.layer.charactercreation.sr.step
        if hasattr(step, 'GoToAssetMode'):
            uthread.new(step.GoToAssetMode, 0, 1)
            if step.sr.tattooMenu and not step.sr.tattooMenu.destroyed:
                step.sr.tattooMenu.Close()
        if hasattr(step, 'LoadFaceMode'):
            uthread.new(step.LoadFaceMode)
        uicore.layer.charactercreation.FadeFromBlack()



    def ClickingOnCurrent(self, id, cont, allConts, animate = False, what = [], *args):
        self.isActive = 1
        expanded = getattr(cont, 'expanded', 0)
        if expanded:
            opacity = 1.0
            selectionOn = 0
        else:
            opacity = 0.3
            selectionOn = 1
        cont.opacity = 1.0
        self.SetSelectionState(cont, on=selectionOn)
        self.ChangeHexOpacity(self.GetMainHexes(exceptWhat=what).values(), opacity=opacity)
        newState = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][expanded]
        self.ChangeStateOfAlmostAllConts(allConts, newState, [id], animate=True)
        cont.expanded = not expanded



    def GetMainHexes(self, exceptWhat = [], *args):
        mainHexes = {text:cont for (text, cont,) in [('race', self.raceConts.get(self.raceID, None)), ('bloodline', self.bloodlineConts.get(self.bloodlineID, None)), ('gender', self.genderConts.get(self.genderID, None))] if text not in exceptWhat}
        return mainHexes



    def ChangeStateOfAlmostAllConts(self, allConts, newState, exceptIDs = [], animate = False):
        changed = []
        doAnimation = animate and newState == uiconst.UI_NORMAL
        for (id, cont,) in allConts.iteritems():
            if id in exceptIDs:
                if newState == uiconst.UI_HIDDEN:
                    cont.expanded = False
                continue
            if not doAnimation:
                cont.state = newState
            changed.append(cont)

        if doAnimation:
            self.AnimateHexes(changed)
        return changed



    def AnimateHexes(self, changedConts, *args):
        for cont in changedConts:
            cont.state = uiconst.UI_HIDDEN

        uthread.new(self._AnimateHexesThread, changedConts, attribute='top')



    def _AnimateHexesThread(self, changedConts, attribute, time = 100.0, *args):
        self._AnimateHexList(changedConts, time=time, attribute=attribute)



    def SetSelectionState(self, cont, on = 1):
        if not cont:
            return 
        if on:
            cont.normalCont.state = uiconst.UI_HIDDEN
            cont.selection.state = uiconst.UI_DISABLED
        else:
            cont.normalCont.state = uiconst.UI_DISABLED
            cont.selection.state = uiconst.UI_HIDDEN



    def CloseAllExtraHexes(self, *args):
        self.ChangeStateOfAlmostAllConts(self.raceConts, uiconst.UI_HIDDEN, [self.raceID], animate=False)
        self.ChangeStateOfAlmostAllConts(self.bloodlineConts, uiconst.UI_HIDDEN, [self.bloodlineID], animate=False)
        self.ChangeStateOfAlmostAllConts(self.genderConts, uiconst.UI_HIDDEN, [self.genderID], animate=False)
        self.ChangeHexOpacity(self.GetMainHexes().values(), opacity=1.0)



    def Disable(self, *args):
        self.state = uiconst.UI_DISABLED
        self.opacity = 0.3



    def Enable(self, *args):
        self.state = uiconst.UI_PICKCHILDREN
        self.opacity = 1.0
        self.ChangeHexOpacity(self.GetMainHexes().values(), opacity=1.0)



    def ChangeHexOpacity(self, hexes, opacity = 1.0):
        for h in hexes:
            h.opacity = opacity
            self.SetSelectionState(h, 0)




    def _OnGlobalMouseUp(self, obj, *args):
        if self.isActive and not isinstance(obj, uicls.CCHexButtonMedium):
            self.CloseAllExtraHexes()
            self.isActive = False
        return 1



    def OnClose_(self, *args):
        uicore.event.UnregisterForTriuiEvents(self.sr.cookie)




class CCHexButtonMedium(uicls.Container):
    __guid__ = 'uicls.CCHexButtonMedium'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/bloodlines.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/bloodlinesInverted.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexBg.dds'
    bevelTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexBevel.dds'
    shawdowTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexShadow.dds'
    numColumns = 4
    hexPadWidth = 0
    hexPadHeight = 0
    wInterval = 64
    hInterval = 64
    rectW = 64
    rectH = 64
    shadowOffset = 1

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.hint = self.hexName = attributes.hexName or ''
        self.info = attributes.info
        self.currState = attributes.state
        self.func = attributes.func
        self.id = attributes.id
        self.iconNum = attributes.iconNum
        self.showIcon = attributes.get('showIcon', 1)
        self.clickable = attributes.get('clickable', 1)
        self.showBg = self.clickable
        self.SetupHex()



    def SetupHex(self, *args):
        (textureNum, logoLocation,) = self.GetLogoLocation()
        normalCont = uicls.Container(name='normal', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        if self.showBg:
            sprite = uicls.Sprite(name='normalBg', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.bgTexture, padding=(-self.hexPadWidth,
             -self.hexPadHeight,
             -self.hexPadWidth,
             -self.hexPadHeight))
            (sprite.SetRGB(0.35, 0.35, 0.35, 0.3),)
            sprite = uicls.Sprite(name='normalBevel', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.bevelTexture, padding=(-self.hexPadWidth,
             -self.hexPadHeight,
             -self.hexPadWidth,
             -self.hexPadHeight))
            sprite.SetAlpha(0.2)
            self.bevel = sprite
        if self.showIcon:
            sprite = uicls.Sprite(name='normalIcon', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'texture_%s' % textureNum, ''))
            (sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight,) = logoLocation
            sprite.SetAlpha(1.0)
            self.logo = sprite
            shadowOffset = getattr(self, 'shadowOffset', 3)
            sprite = uicls.Sprite(name='normalShadow', parent=normalCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'texture_%s' % textureNum, ''), padding=(shadowOffset,
             shadowOffset,
             -shadowOffset,
             -shadowOffset))
            (sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight,) = logoLocation
            sprite.SetRGB(0.0, 0.0, 0.0, 0.3)
        self.normalCont = normalCont
        name = '%sFrame' % self.hexName
        sprite = uicls.Sprite(name=name, parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath=self.frameTexture, padding=(-self.hexPadWidth,
         -self.hexPadHeight,
         -self.hexPadWidth,
         -self.hexPadHeight))
        sprite.SetAlpha(0.2)
        self.frame = sprite
        name = '%sSelection' % self.hexName
        selectionCont = uicls.Container(name='selectionCont', parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        sprite = uicls.Sprite(name=name, parent=selectionCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'textureInv_%s' % textureNum, ''))
        (sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight,) = logoLocation
        sprite = uicls.Sprite(name=name, parent=selectionCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=getattr(self, 'textureInv_%s' % textureNum, ''), padding=(2, 2, -2, -2))
        (sprite.rectLeft, sprite.rectTop, sprite.rectWidth, sprite.rectHeight,) = logoLocation
        sprite.SetRGB(0.0, 0.0, 0.0, 0.3)
        self.selection = selectionCont
        if self.showBg:
            sprite = uicls.Sprite(name='shadow', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self.shawdowTexture, padding=(-self.hexPadWidth,
             -self.hexPadHeight,
             -self.hexPadWidth,
             -self.hexPadHeight))
            sprite.SetAlpha(0.5)



    def OnClick(self, *args):
        if not self.clickable:
            return 
        if self.func:
            self.func(self)



    def OnMouseEnter(self, *args):
        if not self.clickable:
            return 
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))
        if getattr(self, 'frame', None) is not None:
            self.frame.state = uiconst.UI_DISABLED
        if getattr(self, 'bevel', None) is not None:
            self.bevel.SetAlpha(0.5)



    def OnMouseExit(self, *args):
        if not self.clickable:
            return 
        if getattr(self, 'frame', None) is not None:
            self.frame.state = uiconst.UI_HIDDEN
        if getattr(self, 'bevel', None) is not None:
            self.bevel.SetAlpha(0.2)



    def SelectHex(self, allConts = []):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
        for c in allConts:
            c.normalCont.state = uiconst.UI_DISABLED
            c.frame.state = uiconst.UI_HIDDEN
            c.selection.state = uiconst.UI_HIDDEN

        self.normalCont.state = uiconst.UI_HIDDEN
        self.selection.state = uiconst.UI_DISABLED



    def GetLogoLocation(self, *args):
        iconNum = self.iconNum
        numInFile = pow(self.numColumns, 2)
        textureNum = iconNum / numInFile
        newIconNum = iconNum - numInFile * textureNum
        j = newIconNum / self.numColumns
        i = newIconNum % self.numColumns
        leftOffset = getattr(self, 'leftOffset', 0)
        topOffset = getattr(self, 'topOffset', 0)
        top = topOffset + self.hexPadHeight + j * self.hInterval
        left = leftOffset + self.hexPadWidth + i * self.wInterval
        return (textureNum, (left,
          top,
          self.rectW,
          self.rectH))




class CCHexButtonRace2(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonRace2'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexes.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexesInverted.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/hexes/mediumHexBg.dds'
    topOffset = 64


class CCHexButtonGender2(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonGender2'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexes.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/smallRaceGenderHexesInverted.dds'


class CCHexButtonAncestry(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonAncestry'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries1.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted1.dds'
    texture_1 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries2.dds'
    textureInv_1 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted2.dds'
    texture_2 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries3.dds'
    textureInv_2 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted3.dds'


class CCHexButtonSchool(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonSchool'
    texture_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestries3.dds'
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/hexes/ancestriesInverted3.dds'
    topOffset = 192
    leftOffset = 64


class CCHexButtonHead(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonHead'
    texture_0 = ''
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/headPickerBG.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/headPickerFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/headPickerBG.dds'
    bevelTexture = 'res:/UI/Texture/CharacterCreation/headPickerBevel.dds'
    shawdowTexture = 'res:/UI/Texture/CharacterCreation/headPickerShadow.dds'
    numColumns = 1
    shadowOffset = 0


class CCHexButtonBody(CCHexButtonMedium):
    __guid__ = 'uicls.CCHexButtonBody'
    texture_0 = ''
    textureInv_0 = 'res:/UI/Texture/CharacterCreation/bodyPickerBG.dds'
    frameTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerFrame.dds'
    bgTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerBG.dds'
    bevelTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerBevel.dds'
    shawdowTexture = 'res:/UI/Texture/CharacterCreation/bodyPickerShadow.dds'
    numColumns = 1
    shadowOffset = 0
    wInterval = 128
    hInterval = 128
    rectW = 128
    rectH = 128


