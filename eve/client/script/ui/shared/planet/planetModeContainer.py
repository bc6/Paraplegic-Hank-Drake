import uix
import uiconst
import planet
import uicls
import planetCommon
import util
EDITMODECONTAINER_HEIGHT = 110

class PlanetModeContainer(uicls.NeocomContainer):
    __guid__ = 'planet.ui.PlanetModeContainer'
    default_name = 'planetModeContainer'
    __notifyevents__ = ['OnEditModeChanged', 'OnEditModeBuiltOrDestroyed', 'OnPlanetCommandCenterDeployedOrRemoved']
    default_padLeft = 0

    def ApplyAttributes(self, attributes):
        self.mode = None
        uicls.NeocomContainer.ApplyAttributes(self, attributes)
        self.inEditMode = False
        self.CreateLayout()
        sm.RegisterNotify(self)



    def CreateLayout(self):
        self.headerContainer = uicls.Container(parent=self.content, name='headerContainer', align=uiconst.TOTOP, pos=(0, 0, 0, 40))
        self.editModeContainer = uicls.Container(parent=self.content, name='buttonContainer', align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padding=(0, 0, 0, 5))
        self.editModeContent = uicls.Container(parent=self.editModeContainer, name='editModeContent', align=uiconst.TOALL, padding=(10, 6, 10, 6))
        uicls.Fill(parent=self.editModeContainer, color=util.Color.GetGrayRGBA(0.0, 0.3))
        uicls.Frame(parent=self.editModeContainer, color=util.Color.GetGrayRGBA(0.0, 0.2))
        self.tabButtonContainer = uicls.Container(parent=self.content, name='tabButtonContainer', align=uiconst.TOTOP, pos=(0, 0, 0, 28))
        self.tabPanelContainer = uicls.Container(parent=self.content, name='tabPanelContainer', align=uiconst.TOALL, padTop=4)
        self.heading = uicls.Label(text=mls.UI_PI_VIEWING_PLANET, name='heading', parent=self.headerContainer, align=uiconst.TOPLEFT, height=14, state=uiconst.UI_DISABLED)
        self.planetName = uicls.CaptionLabel(text='', align=uiconst.RELATIVE, fontsize=14, parent=self.headerContainer, top=self.heading.textheight, letterspace=5)
        self.resourceControllerTab = planet.ui.ResourceController(parent=self.tabPanelContainer)
        self.editModeTab = planet.ui.PlanetEditModeContainer(parent=self.tabPanelContainer)
        tabs = [[mls.UI_CMD_BUILD,
          self.editModeTab,
          self,
          None,
          'editModeTab'], [mls.UI_PI_SCAN,
          self.resourceControllerTab,
          self,
          None,
          'resourceControllerTab']]
        self.modeButtonGroup = uicls.FlatButtonGroup(parent=self.tabButtonContainer, align=uiconst.TOTOP, height=28, toggleEnabled=False)
        self.modeButtonGroup.Startup(tabs, selectedArgs=['editModeTab'])
        BTNSIZE = 24
        exitBtn = uicls.Button(parent=self, label=mls.UI_PI_CMD_EXIT, align=uiconst.TOPRIGHT, pos=(-6,
         -4,
         BTNSIZE,
         BTNSIZE), icon='ui_73_16_45', iconSize=16, func=self.ExitPlanetMode, alwaysLite=True, color=util.Color.RED)
        exitBtn.hint = mls.UI_PI_EXIT_PLANET_MODE
        homeBtn = uicls.Button(parent=self, label=mls.UI_PI_CMD_HOME, align=uiconst.TOPRIGHT, pos=(exitBtn.width - 10,
         -4,
         BTNSIZE,
         BTNSIZE), icon='ui_73_16_46', iconSize=16, func=self.ViewCommandCenter, alwaysLite=True)
        homeBtn.hint = mls.UI_PI_CMD_HOMEHINT
        self.sr.homeBtn = homeBtn
        self.UpdatePlanetText()
        self.UpdateHomeButton()
        self.CreateEditModeContainer()



    def UpdatePlanetText(self):
        planetUI = sm.GetService('planetUI')
        planetID = planetUI.planetID
        self.planetName.text = '<b>%s</b>' % cfg.evelocations.Get(planetID).locationName.upper()



    def OnButtonSelected(self, mode):
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_general_switch_play')
        if mode == 'resourceControllerTab':
            sm.GetService('planetUI').planetAccessRequired = True



    def ExitPlanetMode(self, *args):
        sm.GetService('planetUI').Close()



    def ViewCommandCenter(self, *args):
        sm.GetService('planetUI').FocusCameraOnCommandCenter()



    def OnEditModeBuiltOrDestroyed(self, *args):
        self.UpdateHomeButton()



    def OnPlanetCommandCenterDeployedOrRemoved(self, *args):
        self.UpdateHomeButton()



    def OnEditModeChanged(self, *args):
        if not self or self.destroyed:
            return 
        self.UpdateHomeButton()



    def UpdateHomeButton(self):
        if session.charid in sm.GetService('planetUI').planet.colonies:
            self.sr.homeBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.homeBtn.state = uiconst.UI_HIDDEN



    def CreateEditModeContainer(self):
        uicls.Label(parent=self.editModeContent, text=mls.UI_PI_EDITSPENDING, align=uiconst.RELATIVE, fontsize=14, uppercase=True, letterspace=1)
        self.powerGauge = uicls.Gauge(parent=self.editModeContent, pos=(0, 22, 125, 34), color=planetCommon.PLANET_COLOR_POWER, label=mls.UI_PI_POWERUSAGE)
        self.cpuGauge = uicls.Gauge(parent=self.editModeContent, pos=(140, 22, 125, 34), color=planetCommon.PLANET_COLOR_CPU, label=mls.UI_PI_CPUUSAGE)
        self.UpdatePowerAndCPUGauges()
        btns = [[mls.UI_CMD_SUBMIT, self.Submit, ()], [mls.UI_CMD_CANCEL, self.Cancel, ()]]
        bottom = uicls.Container(parent=self.editModeContent, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 40))
        btns = uicls.ButtonGroup(btns=btns, subalign=uiconst.CENTERRIGHT, parent=bottom, line=False, alwaysLite=True)
        self.costText = planet.ui.CaptionAndSubtext(parent=bottom, align=uiconst.TOPLEFT, top=13, caption=mls.UI_GENERIC_COST, subtext='')



    def UpdatePowerAndCPUGauges(self):
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(session.charid)
        if not colony or colony.colonyData is None:
            return 
        originalData = sm.GetService('planetUI').GetCurrentPlanet().GetEditModeData()
        if originalData is None:
            origCpu = 0
            origPower = 0
        else:
            origCpu = originalData.GetColonyCpuUsage()
            origPower = originalData.GetColonyPowerUsage()
        cpuOutput = float(colony.colonyData.GetColonyCpuSupply())
        powerOutput = float(colony.colonyData.GetColonyPowerSupply())
        cpu = colony.colonyData.GetColonyCpuUsage()
        power = colony.colonyData.GetColonyPowerUsage()
        cpuDiff = cpu - origCpu
        powerDiff = power - origPower
        cpuUnit = mls.UI_GENERIC_TERAFLOPSSHORT
        powerUnit = mls.UI_GENERIC_MEGAWATTSHORT
        self.cpuGauge.SetValue(cpu / cpuOutput if cpuOutput > 0 else 0)
        self.cpuGauge.HideAllMarkers()
        self.cpuGauge.ShowMarker(origCpu / cpuOutput if cpuOutput > 0 else 0)
        self.powerGauge.SetValue(power / powerOutput if powerOutput > 0 else 0)
        self.powerGauge.HideAllMarkers()
        self.powerGauge.ShowMarker(origPower / powerOutput if powerOutput > 0 else 0)
        sign = ['', '+'][(cpuDiff >= 0)]
        self.cpuGauge.SetSubText('%s%4.2f %s' % (sign, cpuDiff, cpuUnit))
        sign = ['', '+'][(powerDiff >= 0)]
        self.powerGauge.SetSubText('%s%4.2f %s' % (sign, powerDiff, powerUnit))
        self.cpuGauge.hint = mls.UI_PI_EDITATTRIBUTEDIFF % {'current': origCpu,
         'after': cpu,
         'maximum': cpuOutput,
         'unit': cpuUnit}
        self.powerGauge.hint = mls.UI_PI_EDITATTRIBUTEDIFF % {'current': origPower,
         'after': power,
         'maximum': powerOutput,
         'unit': powerUnit}



    def UpdateCostOfCurrentChanges(self):
        cost = sm.GetService('planetUI').GetCurrentPlanet().GetCostOfCurrentEdits()
        import util
        self.costText.SetSubtext(util.FmtISK(cost, showFractionsAlways=0))



    def Submit(self):
        sm.GetService('planetUI').planet.SubmitChanges()
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_submit_play')



    def Cancel(self):
        sm.GetService('planetUI').planet.RevertChanges()
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_cancel_play')



    def OnEditModeChanged(self, isEdit):
        if not self or self.destroyed:
            return 
        if not isEdit:
            uicore.effect.MorphUI(self.editModeContainer, 'opacity', 0.0, time=250.0, newthread=False, float=True)
            if not self or self.destroyed:
                return 
            uicore.effect.MorphUI(self.editModeContainer, 'height', 0, time=250.0, newthread=False)
            if not self or self.destroyed:
                return 
            self.editModeContainer.state = uiconst.UI_HIDDEN
            self.inEditMode = False
        else:
            self.UpdatePowerAndCPUGauges()
            self.UpdateCostOfCurrentChanges()
            self.editModeContainer.height = 0
            self.editModeContainer.opacity = 0.0
            self.editModeContainer.state = uiconst.UI_NORMAL
            EDITMODECONTAINER_HEIGHT = 105
            uicore.effect.MorphUI(self.editModeContainer, 'height', EDITMODECONTAINER_HEIGHT, time=250.0, newthread=False)
            uicore.effect.MorphUI(self.editModeContainer, 'opacity', 1.0, time=250.0, newthread=False, float=True)
            self.inEditMode = True



    def OnEditModeBuiltOrDestroyed(self):
        if not self.inEditMode:
            self.editModeContainer.height = 0
            self.editModeContainer.opacity = 0.0
            self.editModeContainer.state = uiconst.UI_NORMAL
            EDITMODECONTAINER_HEIGHT = 105
            uicore.effect.MorphUI(self.editModeContainer, 'height', EDITMODECONTAINER_HEIGHT, time=250.0, newthread=False)
            uicore.effect.MorphUI(self.editModeContainer, 'opacity', 1.0, time=250.0, newthread=False, float=True)
            self.inEditMode = True
        self.UpdatePowerAndCPUGauges()
        self.UpdateCostOfCurrentChanges()




