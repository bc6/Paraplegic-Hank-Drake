import service
import blue
import xtriui
import util
import uix
import uiutil
import form
import uthread
import listentry
import uicls
import uiconst
import log
import localization
import localizationUtil

class AttributeRespecWindow(uicls.Window):
    __guid__ = 'form.attributeRespecWindow'
    __notifyevents__ = ['OnSessionChanged']
    default_windowID = 'attributerespecification'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.readOnly = attributes.readOnly
        self.SetMinSize([500, 440])
        self.MakeUnResizeable()
        self.SetCaption(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Attributes'))
        self.SetWndIcon('ui_2_64_16')
        self.godma = sm.StartService('godma')
        self.skillHandler = self.godma.GetSkillHandler()
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/NeuralRemapping'), subcaption=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/NeuralRemappingTagline'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.attributes = [const.attributeIntelligence,
         const.attributePerception,
         const.attributeCharisma,
         const.attributeWillpower,
         const.attributeMemory]
        self.implantTypes = [19554,
         19540,
         19555,
         19553,
         19551]
        self.attributeIcons = ['ui_22_32_3',
         'ui_22_32_5',
         'ui_22_32_1',
         'ui_22_32_2',
         'ui_22_32_4']
        self.attributeLabels = [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeIntelligence'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributePerception'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeCharisma'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeWillpower'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeMemory')]
        self.currentAttributes = {}
        self.implantModifier = {}
        self.unspentPts = 0
        self.ConstructLayout()
        self.Load()



    def OnSessionChanged(self, isRemote, session, change):
        self.skillHandler = self.godma.GetSkillHandler()



    def Load(self, *args):
        if not eve.session.charid or not self or self.destroyed:
            return 
        dogmaLM = self.godma.GetDogmaLM()
        attrDict = dogmaLM.GetCharacterBaseAttributes()
        unspentPts = const.respecTotalRespecPoints
        for x in xrange(0, 5):
            attr = self.attributes[x]
            if attr in attrDict:
                attrValue = attrDict[attr]
                if attrValue > const.respecMaximumAttributeValue:
                    attrValue = const.respecMaximumAttributeValue
                if attrValue < const.respecMinimumAttributeValue:
                    attrValue = const.respecMinimumAttributeValue
                self.currentAttributes[attr] = attrValue
                self.respecBar[x].SetValue(attrValue - const.respecMinimumAttributeValue)
                unspentPts -= attrValue
            modifiers = self.skillHandler.GetCharacterAttributeModifiers(attr)
            implantBonus = 0
            for (itemID, typeID, operation, value,) in modifiers:
                categoryID = cfg.invtypes.Get(typeID).categoryID
                if categoryID == const.categoryImplant:
                    implantBonus += value

            totalAttributesText = localizationUtil.FormatNumeric(int(self.currentAttributes[attr]) + implantBonus, decimalPlaces=0)
            self.totalLabels[x].text = '<right>%s</right>' % totalAttributesText
            self.implantModifier[x] = implantBonus
            (label, icon,) = self.implantLabels[x]
            if implantBonus == 0:
                icon.SetAlpha(0.5)
                label.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/ImplantBonusZero')
                label.SetAlpha(0.5)
            else:
                label.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/ImplantBonus', implantBonus=int(implantBonus))

        if not self.readOnly:
            self.unspentPts = unspentPts
            self.sr.unassignedBar.SetValue(unspentPts)
            unspentPtsText = localizationUtil.FormatNumeric(self.unspentPts, decimalPlaces=0)
            self.availableLabel.text = '<right>%s</right>' % unspentPtsText
            if self.unspentPts <= 0:
                self.sr.saveWarningText.state = uiconst.UI_HIDDEN
            else:
                self.sr.saveWarningText.state = uiconst.UI_DISABLED



    def ConstructLayout(self):
        self.sr.topPar = uicls.Container(name='topPar', align=uiconst.TOTOP, parent=self.sr.main, height=64, top=0)
        headingPar = uicls.Container(name='headingPar', align=uiconst.TOBOTTOM, parent=self.sr.topPar, height=14, top=2)
        self.sr.topText = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterRespecMessage'), parent=self.sr.topPar, left=9, width=485, singleLine=0, state=uiconst.UI_NORMAL, top=4)
        self.sr.topPar.height = 28 + self.sr.topText.textheight
        barColor = (0.5, 0.5, 0.5, 0.75)
        c = uicls.Container(name='', align=uiconst.TOTOP, parent=self.sr.main, height=2, top=0)
        uicls.Line(parent=c, align=uiconst.TOALL, left=10, width=10, height=1, color=barColor)
        self.sr.intPar = uicls.Container(name='intPar', align=uiconst.TOTOP, parent=self.sr.main, height=40)
        self.sr.memPar = uicls.Container(name='memPar', align=uiconst.TOTOP, parent=self.sr.main, height=40)
        self.sr.chaPar = uicls.Container(name='chaPar', align=uiconst.TOTOP, parent=self.sr.main, height=40)
        self.sr.perPar = uicls.Container(name='perPar', align=uiconst.TOTOP, parent=self.sr.main, height=40)
        self.sr.wilPar = uicls.Container(name='wilPar', align=uiconst.TOTOP, parent=self.sr.main, height=40)
        if not self.readOnly:
            c = uicls.Container(name='', align=uiconst.TOTOP, parent=self.sr.main, height=2, top=0)
            uicls.Line(parent=c, align=uiconst.TOALL, left=10, width=10, height=1, color=barColor)
            self.sr.bottomPar = uicls.Container(name='bottomPar', align=uiconst.TOTOP, parent=self.sr.main, top=8, height=65)
        else:
            self.sr.bottomPar = uicls.Container(name='bottomPar', align=uiconst.TOTOP, parent=self.sr.main, top=8, height=5)
        leftMargin = 8
        self.attributePars = [self.sr.intPar,
         self.sr.memPar,
         self.sr.chaPar,
         self.sr.perPar,
         self.sr.wilPar]
        self.sprites = []
        iconsize = 32
        for x in xrange(0, 5):
            icon = uicls.Icon(parent=self.attributePars[x], width=iconsize, height=iconsize, size=iconsize, icon=self.attributeIcons[x], left=leftMargin, align=uiconst.TOLEFT)

        leftMargin += iconsize + 3
        self.totalLabels = []
        maxTextWidth = 10
        attributeLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Attributes'), parent=headingPar, singleline=1, left=leftMargin - iconsize / 2)
        for x in xrange(0, 5):
            label1 = uicls.EveLabelMedium(text=self.attributeLabels[x], parent=self.attributePars[x], singleline=1, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, left=leftMargin)
            maxTextWidth = max(label1.textwidth, maxTextWidth)

        leftMargin += maxTextWidth + 20
        baseLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/BaseStatPoints'), parent=headingPar, left=leftMargin, singleline=1)
        for x in xrange(0, 5):
            minText = localizationUtil.FormatNumeric(const.respecMinimumAttributeValue, decimalPlaces=0)
            label2 = uicls.EveLabelMedium(text=minText, parent=self.attributePars[x], width=20, singleline=1, state=uiconst.UI_DISABLED, left=leftMargin + baseLabel.textwidth / 2 - 10, top=10)
            label2.bold = 1

        leftMargin += baseLabel.textwidth + 20
        implantLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterImplants'), parent=headingPar, left=leftMargin, singleline=1)
        self.implantLabels = []
        for x in xrange(0, 5):
            icon = uicls.Icon(parent=self.attributePars[x], width=32, height=32, size=32, icon=util.IconFile(cfg.invtypes.Get(self.implantTypes[x]).iconID), left=leftMargin - 4, align=uiconst.TOPLEFT, ignoreSize=True)
            label2 = uicls.EveLabelMedium(text='', parent=self.attributePars[x], singleline=1, left=leftMargin + 28, top=10)
            self.implantLabels.append((label2, icon))

        boxWidth = 6
        boxHeight = 12
        boxMargin = 1
        boxSpacing = 1
        barHeight = boxHeight + 2 * boxMargin
        backgroundColor = (0.0, 0.0, 0.0, 0.0)
        leftMargin += implantLabel.textwidth
        leftMargin += (450 - (leftMargin + 130)) / 2
        buttonSize = 24
        if not self.readOnly:
            for x in xrange(0, 5):
                minusText = localization.GetByLabel('UI/Common/Buttons/Minus')
                uicls.Button(parent=self.attributePars[x], label=minusText, fixedwidth=buttonSize, pos=(leftMargin,
                 4,
                 0,
                 0), func=self.DecreaseAttribute, args=(x,))

        leftMargin += buttonSize + 4
        numBoxes = const.respecMaximumAttributeValue - const.respecMinimumAttributeValue
        barWidth = numBoxes * boxSpacing + 2 * boxMargin + numBoxes * boxWidth - 1
        remappableLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/RemappableStat'), parent=headingPar, left=leftMargin, singleline=1)
        remappableLabel.left = remappableLabel.left - remappableLabel.textwidth / 2 + barWidth / 2
        colorDict = {uicls.ClickableBoxBar.COLOR_UNSELECTED: (0.2, 0.2, 0.2, 1.0),
         uicls.ClickableBoxBar.COLOR_SELECTED: (0.2, 0.8, 0.2, 1.0)}
        self.respecBar = []
        for x in xrange(0, 5):
            bar = uicls.Container(parent=self.attributePars[x], align=uiconst.TOPLEFT, left=leftMargin, top=7, width=barWidth, height=barHeight)
            bar.state = uiconst.UI_PICKCHILDREN
            bar = uicls.ClickableBoxBar(parent=bar, numBoxes=numBoxes, boxWidth=boxWidth, boxHeight=boxHeight, boxMargin=boxMargin, boxSpacing=boxSpacing, backgroundColor=backgroundColor, colorDict=colorDict)
            bar.OnValueChanged = self.OnMemberBoxClick
            bar.OnAttemptBoxClicked = self.ValidateBoxClick
            self.respecBar.append(bar)

        leftMargin += barWidth + 4
        if not self.readOnly:
            for x in xrange(0, 5):
                plusText = localization.GetByLabel('UI/Common/Buttons/Plus')
                uicls.Button(parent=self.attributePars[x], label=plusText, fixedwidth=24, pos=(leftMargin,
                 4,
                 0,
                 0), func=self.IncreaseAttribute, args=(x,))

        barEnd = leftMargin
        leftMargin += buttonSize + 20
        leftMargin = 450
        totalLabel = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/StatTotal'), parent=headingPar, left=leftMargin, singleline=1)
        totalLabelPos = leftMargin + totalLabel.textwidth / 2 - 15
        for x in xrange(0, 5):
            label3 = uicls.EveLabelMedium(name='', parent=self.attributePars[x], width=20, singleline=1, left=totalLabelPos, top=10)
            label3.bold = 1
            self.totalLabels.append(label3)

        if not self.readOnly:
            textObj = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/UnassignedAttributePoints'), parent=self.sr.bottomPar, left=16)
            numBoxes = const.respecTotalRespecPoints - const.respecMinimumAttributeValue * 5
            barWidth = numBoxes * boxSpacing + 2 * boxMargin + numBoxes * boxWidth - 1
            colorDict = {uicls.ClickableBoxBar.COLOR_UNSELECTED: (0.2, 0.2, 0.2, 1.0),
             uicls.ClickableBoxBar.COLOR_SELECTED: (0.2, 0.8, 0.2, 1.0)}
            self.sr.unassignedBar = uicls.Container(parent=self.sr.bottomPar, align=uiconst.TOPLEFT, left=barEnd - barWidth + 24, top=0, width=barWidth, height=barHeight)
            self.sr.unassignedBar.state = uiconst.UI_PICKCHILDREN
            self.sr.unassignedBar = uicls.ClickableBoxBar(parent=self.sr.unassignedBar, numBoxes=numBoxes, boxWidth=boxWidth, boxHeight=boxHeight, boxMargin=boxMargin, boxSpacing=boxSpacing, backgroundColor=backgroundColor, colorDict=colorDict, readonly=True, hintFormat='UI/CharacterSheet/CharacterSheetWindow/Attributes/UnassignedPointsHint')
            self.availableLabel = uicls.EveLabelMedium(text='', parent=self.sr.bottomPar, width=20, singleline=1, left=totalLabelPos)
            self.sr.saveWarningText = uicls.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CannotSaveUnassignedPoints'), parent=self.sr.bottomPar, left=16, top=16, color=(1.0, 0.0, 0.0, 0.9))
            btns = uicls.ButtonGroup(btns=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/SaveStatChanges'),
              self.SaveChanges,
              (),
              None], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
              self.CloseByUser,
              (),
              None]], parent=self.sr.main, idx=0)
        heightTotal = self.sr.topParent.height + self.sr.headerParent.height
        for child in self.sr.main.children:
            (width, height,) = child.GetAbsoluteSize()
            heightTotal += height

        self.SetMinSize([self.GetMinWidth(), heightTotal], refresh=1)



    def SaveChanges(self, *args):
        totalAttrs = 0
        newAttributes = {}
        for x in xrange(0, 5):
            newAttributes[self.attributes[x]] = const.respecMinimumAttributeValue + self.respecBar[x].GetValue()

        for attrValue in newAttributes.itervalues():
            if attrValue < const.respecMinimumAttributeValue:
                raise UserError('RespecAttributesTooLow')
            elif attrValue > const.respecMaximumAttributeValue:
                raise UserError('RespecAttributesTooHigh')
            totalAttrs += attrValue

        if totalAttrs != const.respecTotalRespecPoints or self.sr.unassignedBar.GetValue() > 0:
            self.sr.saveWarningText.state = uiconst.UI_DISABLED
            raise UserError('RespecAttributesMisallocated')
        allSame = True
        for attr in self.attributes:
            if int(self.currentAttributes[attr]) != int(newAttributes[attr]):
                allSame = False
                break

        if not allSame:
            respecInfo = sm.GetService('skills').GetRespecInfo()
            freeRespecs = respecInfo['freeRespecs']
            if freeRespecs > 1:
                if eve.Message('ConfirmRespecFree', {'freerespecs': int(respecInfo['freeRespecs']) - 1}, uiconst.YESNO) != uiconst.ID_YES:
                    return 
            elif eve.Message('ConfirmRespec2', {'months': int(const.respecTimeInterval / MONTH)}, uiconst.YESNO) != uiconst.ID_YES:
                return 
            self.skillHandler.RespecCharacter(newAttributes[const.attributeCharisma], newAttributes[const.attributeIntelligence], newAttributes[const.attributeMemory], newAttributes[const.attributePerception], newAttributes[const.attributeWillpower])
        self.CloseByUser()



    def IncreaseAttribute(self, attribute, *args):
        if self.respecBar[attribute].GetValue() >= const.respecMaximumAttributeValue - const.respecMinimumAttributeValue:
            return 
        if self.unspentPts <= 0:
            raise UserError('RespecCannotIncrementNotEnoughPoints')
        if not self.respecBar[attribute].Increment():
            raise UserError('RespecAttributesTooHigh')



    def DecreaseAttribute(self, attribute, *args):
        if self.respecBar[attribute].GetValue() <= 0:
            return 
        if not self.respecBar[attribute].Decrement():
            raise UserError('RespecAttributesTooLow')



    def ValidateBoxClick(self, oldValue, newValue):
        if self.readOnly:
            return False
        if oldValue >= newValue:
            return True
        if self.unspentPts < newValue - oldValue:
            return False
        return True



    def OnMemberBoxClick(self, oldValue, newValue):
        if oldValue is None or oldValue == newValue:
            return 
        if self.readOnly:
            return 
        self.unspentPts -= newValue - oldValue
        self.sr.unassignedBar.SetValue(self.unspentPts)
        unspentPtsText = localizationUtil.FormatNumeric(self.unspentPts, decimalPlaces=0)
        self.availableLabel.text = '<right>%s</right>' % unspentPtsText
        for x in xrange(0, 5):
            totalPts = const.respecMinimumAttributeValue + self.respecBar[x].GetValue() + self.implantModifier[x]
            totalPtsText = localizationUtil.FormatNumeric(int(totalPts), decimalPlaces=0)
            self.totalLabels[x].text = '<right>%s</right>' % totalPtsText

        if self.unspentPts <= 0:
            self.sr.saveWarningText.state = uiconst.UI_HIDDEN




class AttributeRespecEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.AttributeRespec'
    ENTRYHEIGHT = 44

    def Startup(self, *args):
        self.sr.selection = None
        self.sr.hilite = None
        self.OnSelectCallback = None
        self.sr.label = uicls.EveLabelSmall(text=localization.GetByLabel('UI/Neocom/NextDNAModification'), parent=self, left=8, top=4, singleline=1)
        self.sr.respecTime = uicls.EveLabelMedium(text='', parent=self, left=8, top=18, singleline=1)
        self.sr.respecButton = uicls.Button(parent=self, label=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/RemapStatsNow'), align=uiconst.TOPRIGHT, pos=(2, 16, 0, 0), func=self.OpenRespecWindow, args=(False,))
        self.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterSheetHint')



    def Load(self, node):
        self.sr.node = node
        respecsLeft = 0
        freeRespecs = node.Get('freeRespecs', 0)
        if freeRespecs > 1:
            respecsLeft = node.freeRespecs
            self.sr.respecTime.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/NumberOfRemaps', remap=respecsLeft)
            self.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterSheetHintFree')
        elif freeRespecs > 0 or node.time < blue.os.GetWallclockTime():
            self.sr.respecTime.text = localization.GetByLabel('UI/Generic/Now')
        else:
            self.sr.respecTime.text = util.FmtDate(node.time)
            self.sr.respecButton.SetLabel(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributesOverview'))
            self.sr.respecButton.args = (True,)
            self.refreshThread = uthread.new(self.RefreshThread)



    def OpenRespecWindow(self, readOnly, *args):
        wnd = form.attributeRespecWindow.GetIfOpen()
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
        else:
            form.attributeRespecWindow.Open(readOnly=readOnly)



    def RefreshThread(self):
        if not self or self.destroyed:
            return 
        sleepMsec = max(self.sr.node.time - blue.os.GetWallclockTime(), 0) / 10000L
        sleepMsec = min(sleepMsec, 60000)
        while sleepMsec > 0:
            blue.pyos.synchro.SleepWallclock(sleepMsec)
            if not self or self.destroyed:
                return 
            sleepMsec = max(self.sr.node.time - blue.os.GetWallclockTime(), 0) / 10000L
            sleepMsec = min(sleepMsec, 60000)

        if not self or self.destroyed:
            return 
        self.sr.respecButton.state = uiconst.UI_NORMAL
        self.sr.respecTime.text = localization.GetByLabel('UI/Generic/Now')




