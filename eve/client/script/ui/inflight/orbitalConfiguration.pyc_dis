#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/inflight/orbitalConfiguration.py
import uicls
import util
import uiconst
import localization
import moniker

class OrbitalConfigurationWindow(uicls.Window):
    __guid__ = 'form.OrbitalConfigurationWindow'
    default_windowID = 'configureOrbital'
    default_topParentHeight = 0
    default_clipChildren = 1
    WIDTH_COLLAPSED = 270
    WIDTH_EXPANDED = 445
    HEIGHT = 190
    HOVER_ALPHA = 1.0
    NORMAL_ALPHA = 0.8

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        orbitalItem = attributes.get('orbitalItem')
        if not util.IsOrbital(orbitalItem.categoryID):
            raise RuntimeError('Cannot open an orbital configuration window for a non-orbital')
        self.locationID = orbitalItem.locationID
        self.orbitalID = orbitalItem.itemID
        self.typeID = orbitalItem.typeID
        self.remoteOrbitalRegistry = moniker.GetPlanetOrbitalRegistry(self.locationID)
        self.orbitalData = self.remoteOrbitalRegistry.GetSettingsInfo(self.orbitalID)
        self.selectedHour, self.taxRateValues, self.standingLevel, self.allowAlliance, self.allowStandings = self.orbitalData
        self.taxRates = [util.KeyVal(key='corporation'),
         util.KeyVal(key='alliance'),
         util.KeyVal(key='standingHorrible', standing=const.contactHorribleStanding),
         util.KeyVal(key='standingBad', standing=const.contactBadStanding),
         util.KeyVal(key='standingNeutral', standing=const.contactNeutralStanding),
         util.KeyVal(key='standingGood', standing=const.contactGoodStanding),
         util.KeyVal(key='standingHigh', standing=const.contactHighStanding)]
        for taxRate in self.taxRates:
            taxRate.value = getattr(self.taxRateValues, taxRate.key)

        self.variance = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(self.typeID, const.attributeReinforcementVariance)
        self.reinforceHours = [ ('%.2d:00 - %.2d:00' % ((x - self.variance / 3600) % 24, (x + self.variance / 3600) % 24), x) for x in xrange(0, 24) ]
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is not None and self.orbitalID in ballpark.slimItems:
            planetName = cfg.evelocations.Get(ballpark.slimItems[self.orbitalID].planetID).name
            caption = localization.GetByLabel('UI/PI/Common/PlanetaryCustomsOfficeName', planetName=planetName)
        else:
            caption = localization.GetByLabel('UI/DustLink/OrbitalConfiguration')
        self.effects = uicls.UIEffects()
        self.scope = 'inflight'
        self.SetWndIcon('ui_9_64_16', size=32)
        self.SetMinSize([self.WIDTH_COLLAPSED, self.HEIGHT])
        self.SetCaption(caption)
        self.MakeUnResizeable()
        self.Layout()
        self.Redraw()

    def Layout(self):
        self.reinforcementLabel = uicls.EveLabelSmall(text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/ReinforcementExit'), align=uiconst.TOPLEFT, parent=self.sr.main, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/ReinforcementExitTooltip', typeID=self.typeID), left=15, top=13)
        self.reinforceHourCombo = uicls.Combo(parent=self.sr.main, name='orbitalReinforceHourCombo', align=uiconst.TOPLEFT, select=self.selectedHour, options=self.reinforceHours, width=110, height=20, left=140, top=10, padding=(0, 0, 0, 0))
        self.corporationContainer = uicls.Container(align=uiconst.TOPLEFT, parent=self.sr.main, width=self.WIDTH_COLLAPSED, height=25, top=36)
        self.corporationLabel = uicls.EveLabelSmall(text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/CorporationTax'), parent=self.corporationContainer, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/StandingTooltip', typeID=self.typeID), left=15, top=4)
        self.LayoutTaxInput(self.taxRates[0], self.corporationContainer, 140, 0)
        self.allianceContainer = uicls.Container(align=uiconst.TOPLEFT, parent=self.sr.main, width=220, height=25, top=62)
        self.allianceCheckbox = uicls.Checkbox(parent=self.allianceContainer, text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/AllianceTax'), checked=self.allowAlliance, padding=(13, 0, 0, 0), callback=self.Redraw)
        self.LayoutTaxInput(self.taxRates[1], self.allianceContainer, 140, 0)
        self.standingsCheckboxContainer = uicls.Container(align=uiconst.TOPLEFT, parent=self.sr.main, width=220, height=25, top=88)
        self.standingsCheckbox = uicls.Checkbox(parent=self.standingsCheckboxContainer, text=localization.GetByLabel('UI/PI/OrbitalConfigurationWindow/Standing'), checked=self.allowStandings, padding=(13, 0, 0, 0), callback=self.Redraw)
        self.standingsContainer = uicls.Container(name='standingsContainer', parent=self.sr.main, align=uiconst.TOPLEFT, padding=(0, 0, 0, 0), left=self.WIDTH_COLLAPSED, width=self.WIDTH_EXPANDED - self.WIDTH_COLLAPSED, height=144, opacity=0)
        uicls.Line(parent=self.standingsContainer, align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.25))
        self.standingLevelSelector = uicls.StandingLevelSelector(name='standingLevelSelector', parent=self.standingsContainer, align=uiconst.TOPLEFT, level=self.standingLevel, padding=(20, 0, 0, 0), width=90, height=200, top=10, vertical=True, callback=self.Redraw)
        for i, taxRate in enumerate(self.taxRates[2:]):
            self.LayoutTaxInput(taxRate, self.standingsContainer, 50, 10 + i * 26)

        self.footer = uicls.Container(parent=self.sr.main, name='footer', align=uiconst.TOBOTTOM, height=32)
        btns = [(localization.GetByLabel('UI/Common/Submit'), self.Submit, None), (localization.GetByLabel('UI/Common/Cancel'), self.Cancel, None)]
        uicls.ButtonGroup(btns=btns, subalign=uiconst.CENTER, parent=self.footer, line=True, alwaysLite=False)
        self.width = [self.WIDTH_COLLAPSED, self.WIDTH_EXPANDED][int(self.standingsCheckbox.GetValue())]

    def LayoutTaxInput(self, taxRate, parent, left = 0, top = 0):
        taxRateValue = taxRate.value
        taxRateInput = uicls.SinglelineEdit(parent=parent, name='taxRateEdit', align=uiconst.TOPLEFT, setvalue='' if taxRateValue is None else str(100 * taxRateValue), width=90, left=left, top=top, idx=0)
        taxRatePercent = uicls.EveLabelMedium(align=uiconst.TOPLEFT, text='%', parent=parent, left=left + 97, top=top + 2)
        taxRateInput.FloatMode(minfloat=0, maxfloat=100)
        taxRate.input = taxRateInput

    def OnMouseEnterInteractable(self, obj, *args):
        obj.SetOpacity(self.HOVER_ALPHA)

    def OnMouseExitInteractable(self, obj, *args):
        obj.SetOpacity(self.NORMAL_ALPHA)

    def Redraw(self, *args):
        level = self.standingLevelSelector.GetValue()
        taxRateVisible = True
        for taxRate in self.taxRates[2:]:
            if taxRate.standing == level:
                taxRateVisible = False
            self.SetTaxRateVisible(taxRate.input, taxRateVisible)

        self.SetTaxRateVisible(self.taxRates[1].input, not self.allianceCheckbox.GetValue())
        if self.standingsCheckbox.GetValue():
            self.ResizeWindowWidth(self.WIDTH_EXPANDED)
            self.ShowElement(self.standingsContainer)
        else:
            self.HideElement(self.standingsContainer)
            self.ResizeWindowWidth(self.WIDTH_COLLAPSED)

    def ResizeWindowWidth(self, width):
        self.effects.MorphUIMassSpringDamper(self, 'width', width, newthread=True, float=0, dampRatio=0.99, frequency=15.0)

    def HideElement(self, element):
        self.effects.MorphUIMassSpringDamper(element, 'opacity', 0, dampRatio=0.99, frequency=30.0)

    def ShowElement(self, element):
        self.effects.MorphUIMassSpringDamper(element, 'opacity', 1, dampRatio=0.99, frequency=30.0)

    def SetTaxRateVisible(self, field, visible):
        if visible and field.state == uiconst.UI_NORMAL:
            field.hiddenValue = field.GetValue()
            field.SetText(localization.GetByLabel('UI/PI/Common/CustomsOfficeAccessDenied'))
            field.SelectNone()
            field.state = uiconst.UI_DISABLED
            field.sr.text.SetAlpha(0.5)
            self.effects.MorphUIMassSpringDamper(field, 'opacity', 0.5, dampRatio=0.99)
        elif not visible and field.state == uiconst.UI_DISABLED:
            field.SetValue(field.hiddenValue)
            field.hiddenValue = None
            field.state = uiconst.UI_NORMAL
            field.sr.text.SetAlpha(1)
            self.effects.MorphUIMassSpringDamper(field, 'opacity', 1, dampRatio=0.99)

    def GetTaxRateValue(self, field):
        value = getattr(field, 'hiddenValue', None) or field.GetValue()
        return value / 100

    def Submit(self, *args):
        standingValue = self.standingLevelSelector.GetValue()
        allowAllianceValue = self.allianceCheckbox.GetValue()
        allowStandingsValue = self.standingsCheckbox.GetValue()
        reinforceValue = int(self.reinforceHourCombo.GetValue())
        taxRateValues = util.KeyVal({taxRate.key:self.GetTaxRateValue(taxRate.input) for taxRate in self.taxRates})
        remoteOrbitalRegistry = moniker.GetPlanetOrbitalRegistry(self.locationID)
        remoteOrbitalRegistry.UpdateSettings(self.orbitalID, reinforceValue, taxRateValues, standingValue, allowAllianceValue, allowStandingsValue)
        self.CloseByUser()

    def Cancel(self, *args):
        self.CloseByUser()