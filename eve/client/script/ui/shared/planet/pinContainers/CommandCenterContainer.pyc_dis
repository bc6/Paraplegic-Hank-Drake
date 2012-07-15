#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/planet/pinContainers/CommandCenterContainer.py
import uix
import uiconst
import util
import planetCommon
import uicls
import planet
import blue
import uthread
import const
import uiutil
import listentry
import skillUtil
import localization

class CommandCenterContainer(planet.ui.StorageFacilityContainer):
    __guid__ = 'planet.ui.CommandCenterContainer'
    default_name = 'CommandCenterContainer'

    def ApplyAttributes(self, attributes):
        planet.ui.StorageFacilityContainer.ApplyAttributes(self, attributes)

    def _GetInfoCont(self):
        p = self.infoContPad
        infoCont = self._DrawAlignTopCont(110, 'infoCont', padding=(p,
         p,
         p,
         p))
        self.storageGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_STORAGE, label=localization.GetByLabel('UI/PI/Common/Capacity'), top=0)
        self.launchTimeTxt = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/NextLaunchTime'), top=45)
        self.cooldownTimer = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/NextTransferAvailable'), top=80)
        self.cpuGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_CPU, left=self.infoContRightColAt, top=0)
        self.powerGauge = uicls.Gauge(parent=infoCont, value=0.0, color=planetCommon.PLANET_COLOR_POWER, left=self.infoContRightColAt, top=40)
        self.upgradeLevelGauge = uicls.Gauge(parent=infoCont, value=self._GetUpgradeLevelGaugeValue(), color=planetCommon.PLANET_COLOR_CURRLEVEL, backgroundColor=util.Color.GetGrayRGBA(0.5, 0.5), label=localization.GetByLabel('UI/PI/Common/UpgradeLevel'), left=self.infoContRightColAt, top=80)
        self.upgradeLevelGauge.ShowMarkers([0.167,
         0.333,
         0.5,
         0.667,
         0.833], color=util.Color.BLACK)
        return infoCont

    def _UpdateInfoCont(self):
        nextLaunchTime = self.pin.GetNextLaunchTime()
        if nextLaunchTime is not None and nextLaunchTime > blue.os.GetWallclockTime():
            nextLaunchTime = util.FmtTime(nextLaunchTime - blue.os.GetWallclockTime())
        else:
            nextLaunchTime = localization.GetByLabel('UI/Common/Now')
        self.launchTimeTxt.SetSubtext(nextLaunchTime)
        self.storageGauge.SetValue(float(self.pin.capacityUsed) / self.pin.GetCapacity())
        self.storageGauge.SetSubText(localization.GetByLabel('UI/PI/Common/StorageUsed', capacityUsed=self.pin.capacityUsed, capacityMax=self.pin.GetCapacity()))
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(self.pin.ownerID)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Unable to find colony to update info container')
        cpuUsage = colony.colonyData.GetColonyCpuUsage()
        cpuSupply = colony.colonyData.GetColonyCpuSupply()
        if cpuSupply > 0:
            percentage = min(1.0, float(cpuUsage) / cpuSupply)
        else:
            percentage = 0.0
        self.cpuGauge.SetValue(percentage)
        self.cpuGauge.SetText(localization.GetByLabel('UI/PI/Common/CPUPercentage', usedPercentage=percentage * 100))
        self.cpuGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CPUUsed', teraFlopsUsed=int(cpuUsage), teraFlopsMax=cpuSupply))
        powerUsage = colony.colonyData.GetColonyPowerUsage()
        powerSupply = colony.colonyData.GetColonyPowerSupply()
        if powerSupply > 0:
            percentage = min(1.0, float(powerUsage) / powerSupply)
        else:
            percentage = 0.0
        self.powerGauge.SetValue(percentage)
        self.powerGauge.SetText(localization.GetByLabel('UI/PI/Common/PowerPercentage', usedPercentage=percentage * 100))
        self.powerGauge.SetSubText(localization.GetByLabel('UI/PI/Common/PowerUsed', megaWattsUsed=int(powerUsage), megaWattsMax=powerSupply))
        self.upgradeLevelGauge.SetValue(self._GetUpgradeLevelGaugeValue())
        if self.pin.lastRunTime is None or self.pin.lastRunTime <= blue.os.GetWallclockTime():
            self.cooldownTimer.SetSubtext(localization.GetByLabel('UI/Common/Now'))
        else:
            self.cooldownTimer.SetSubtext(util.FmtTime(self.pin.lastRunTime - blue.os.GetWallclockTime()))

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_UPGRADE, panelCallback=self.PanelUpgrade), util.KeyVal(id=planetCommon.PANEL_LAUNCH, panelCallback=self.PanelLaunch), util.KeyVal(id=planetCommon.PANEL_STORAGE, panelCallback=self.PanelShowStorage)]
        btns.extend(planet.ui.BasePinContainer._GetActionButtons(self))
        return btns

    def _GetUpgradeLevelGaugeValue(self):
        currLevel = self.planetUISvc.planet.GetCommandCenterLevel(session.charid)
        return float(currLevel + 1) / (planetCommon.PLANET_COMMANDCENTERMAXLEVEL + 1)

    def PanelLaunch(self):
        self.ResetPayloadContents()
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 272), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        self.contentsScroll = uicls.Scroll(parent=cont, name='contentsScroll', align=uiconst.TOTOP, height=100)
        self.contentsScroll.HideUnderLay()
        uicls.Frame(parent=self.contentsScroll, color=(1.0, 1.0, 1.0, 0.2))
        self.launchTextCont = uicls.Container(name='launchTextContainer', parent=cont, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 100, 200, 50))
        self.launchText = uicls.Label(text='3', parent=self.launchTextCont, align=uiconst.TOALL, fontsize=48, state=uiconst.UI_HIDDEN)
        costCont = uicls.Container(parent=cont, pos=(0, 6, 0, 20), align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.costText = uicls.EveLabelMedium(text='', parent=costCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        btnCont = uicls.Container(parent=cont, pos=(0, 6, 0, 20), align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        manipBtns = [[localization.GetByLabel('UI/PI/Common/Add'), self._AddCommodities, None], [localization.GetByLabel('UI/PI/Common/Remove'), self._RemCommodities, None]]
        self.manipBtns = uicls.ButtonGroup(btns=manipBtns, parent=btnCont, line=False, alwaysLite=True)
        self.payloadScroll = uicls.Scroll(parent=cont, name='payloadScroll', align=uiconst.TOTOP, height=100)
        self.payloadScroll.HideUnderLay()
        uicls.Frame(parent=self.payloadScroll, color=(1.0, 1.0, 1.0, 0.2))
        self._ReloadScrolls()
        self.countdownCont = uicls.Container(parent=cont, pos=(0, 0, 0, 35), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        btns = [[localization.GetByLabel('UI/PI/Common/GoForLaunch'), self._DoLaunch, None], [localization.GetByLabel('UI/PI/Common/ScrubLaunch'), self._CancelLaunch, None]]
        self.launchBtns = uicls.ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
        return cont

    def _ReloadScrolls(self):
        scrolllist = []
        for typeID, amount in self.contentsCommodities.iteritems():
            data = util.KeyVal()
            data.label = '<t>%s<t>%s' % (cfg.invtypes.Get(typeID).name, amount)
            data.typeID = typeID
            data.itemID = None
            data.getIcon = True
            sortBy = amount
            scrolllist.append((sortBy, listentry.Get('Item', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.contentsScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/StorehouseIsEmpty'), headers=['', localization.GetByLabel('UI/PI/Common/Type'), localization.GetByLabel('UI/Common/Quantity')])
        scrolllist = []
        for typeID, amount in self.payloadCommodities.iteritems():
            data = util.KeyVal()
            data.label = '<t>%s<t>%s' % (cfg.invtypes.Get(typeID).name, amount)
            data.typeID = typeID
            data.itemID = None
            data.getIcon = True
            sortBy = amount
            scrolllist.append((sortBy, listentry.Get('Item', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.payloadScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/PayloadIsEmpty'), headers=['', localization.GetByLabel('UI/PI/Common/Type'), localization.GetByLabel('UI/Common/Quantity')])
        self.costText.text = localization.GetByLabel('UI/PI/Common/LaunchCost', iskAmount=util.FmtISK(self.pin.GetExportTax(self.payloadCommodities)))

    def _DoLaunch(self, *args):
        if len(self.payloadCommodities) < 1:
            raise UserError('PleaseSelectCommoditiesToLaunch')
        if not self.pin.CanLaunch(self.payloadCommodities):
            raise UserError('CannotLaunchCommandPinNotReady')
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            raise UserError('CannotLaunchInEditMode')
        if len(self.payloadCommodities) > 0:
            self._ToggleButtons()
            uthread.new(self._LaunchThread)

    def _LaunchThread(self):
        if not self or self.destroyed:
            return
        countdown = 3
        while countdown > 0:
            if not self or self.destroyed:
                return
            self.launchText.state = uiconst.UI_HIDDEN
            self.launchTextCont.width = uix.GetTextWidth(str(countdown), fontsize=48)
            self.launchText.text = str(countdown)
            self.launchText.state = uiconst.UI_DISABLED
            self.launchTextCont.opacity = 1.0
            sm.GetService('audio').SendUIEvent('wise:/msg_pi_spaceports_countdown_play')
            uix.FadeCont(self.launchTextCont, 0, after=0, fadeTime=900.0)
            blue.pyos.synchro.SleepWallclock(100)
            countdown -= 1

        if not self or self.destroyed:
            return
        self.launchText.state = uiconst.UI_HIDDEN
        self.launchTextCont.width = uix.GetTextWidth('UI/PI/Common/LaunchSuccessText', fontsize=48)
        self.launchText.text = localization.GetByLabel('UI/PI/Common/LaunchSuccessText')
        self.launchText.state = uiconst.UI_DISABLED
        self.launchTextCont.opacity = 1.0
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_spaceports_launch_play')
        blue.pyos.synchro.SleepWallclock(500)
        try:
            self.launchText.state = uiconst.UI_HIDDEN
            self.planetUISvc.myPinManager.LaunchCommodities(self.pin.id, self.payloadCommodities)
        except UserError:
            self.ResetPayloadContents()
            self._ReloadScrolls()
            raise 
        finally:
            self._ToggleButtons()

        self._CancelLaunch()

    def _CancelLaunch(self, *args):
        self.ShowPanel(self.PanelLaunch, localization.GetByLabel('UI/PI/Common/Launch'))

    def _ToggleButtons(self):
        if self.launchBtns.state == uiconst.UI_HIDDEN:
            self.launchBtns.state = uiconst.UI_PICKCHILDREN
        else:
            self.launchBtns.state = uiconst.UI_HIDDEN
        if self.manipBtns.state == uiconst.UI_HIDDEN:
            self.manipBtns.state = uiconst.UI_PICKCHILDREN
        else:
            self.manipBtns.state = uiconst.UI_HIDDEN

    def ResetPayloadContents(self):
        self.contentsCommodities = self.pin.GetContents()
        self.payloadCommodities = {}

    def _AddCommodities(self, *args):
        selected = self.contentsScroll.GetSelected()
        toMove = {}
        for entry in selected:
            toMove[entry.typeID] = self.contentsCommodities[entry.typeID]

        for typeID, qty in toMove.iteritems():
            self.contentsCommodities[typeID] -= qty
            if self.contentsCommodities[typeID] <= 0:
                del self.contentsCommodities[typeID]
            if typeID not in self.payloadCommodities:
                self.payloadCommodities[typeID] = 0
            self.payloadCommodities[typeID] += qty

        self._ReloadScrolls()

    def _RemCommodities(self, *args):
        selected = self.payloadScroll.GetSelected()
        toMove = {}
        for entry in selected:
            toMove[entry.typeID] = self.payloadCommodities[entry.typeID]

        for typeID, qty in toMove.iteritems():
            self.payloadCommodities[typeID] -= qty
            if self.payloadCommodities[typeID] <= 0:
                del self.payloadCommodities[typeID]
            if typeID not in self.contentsCommodities:
                self.contentsCommodities[typeID] = 0
            self.contentsCommodities[typeID] += qty

        self._ReloadScrolls()

    def _DrawStoredCommoditiesIcons(self):
        pass

    def PanelUpgrade(self):
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 140), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        self.currLevel = self.planetUISvc.planet.GetCommandCenterLevel(session.charid)
        self.newLevel = self.currLevel
        self.currPowerOutput = self.pin.GetPowerOutput()
        self.maxPowerOutput = float(planetCommon.GetPowerOutput(level=planetCommon.PLANET_COMMANDCENTERMAXLEVEL))
        self.currCPUOutput = self.pin.GetCpuOutput()
        self.maxCPUOutput = float(planetCommon.GetCPUOutput(level=planetCommon.PLANET_COMMANDCENTERMAXLEVEL))
        colorDict = {uicls.ClickableBoxBar.COLOR_BELOWMINIMUM: planetCommon.PLANET_COLOR_CURRLEVEL,
         uicls.ClickableBoxBar.COLOR_SELECTED: planetCommon.PLANET_COLOR_UPGRADELEVEL,
         uicls.ClickableBoxBar.COLOR_UNSELECTED: util.Color.GetGrayRGBA(0.4, alpha=0.7),
         uicls.ClickableBoxBar.COLOR_ABOVEMAXIMUM: (1.0, 0.0, 0.0, 0.25)}
        boxBarCont = uicls.Container(parent=cont, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pos=(0,
         0,
         self.width - 15,
         18))
        upgradeSkill = sm.GetService('skills').GetMySkillsFromTypeID(const.typeCommandCenterUpgrade)
        upgradeSkillLevel = 0
        if upgradeSkill is not None:
            upgradeSkillLevel = upgradeSkill.skillLevel
        boxBar = uicls.ClickableBoxBar(parent=boxBarCont, numBoxes=6, boxValues=range(0, 6), boxWidth=(self.width - 20) / 6, boxHeight=boxBarCont.height - 4, readonly=False, backgroundColor=(0.0, 0.0, 0.0, 0.0), colorDict=colorDict, minimumValue=self.currLevel + 1, hintformat=None, maximumValue=upgradeSkillLevel, aboveMaxHint=localization.GetByLabel('UI/PI/Common/UpgradeFailedInsufficientSkill', skillName=cfg.invtypes.Get(const.typeCommandCenterUpgrade).name))
        boxBar.OnValueChanged = self.OnUpgradeBarValueChanged
        boxBar.OnAttemptBoxClicked = self.OnUpgradeBarBoxClicked
        self.upgradeText = planet.ui.CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/NoUpgradeSelected'), top=boxBarCont.height + 2, width=self.width)
        if self.currLevel == planetCommon.PLANET_COMMANDCENTERMAXLEVEL:
            self.upgradeText.SetCaption(localization.GetByLabel('UI/PI/Common/MaximumUpgradeLevelReached'))
            cont.height = 40
            return cont
        powerValue = float(self.currPowerOutput) / self.maxPowerOutput
        self.upgradePowerGauge = uicls.GaugeMultiValue(parent=cont, value=0.0, colors=[planetCommon.PLANET_COLOR_POWER, planetCommon.PLANET_COLOR_POWERUPGRADE], values=[powerValue, 0.0], label=localization.GetByLabel('UI/PI/Common/PowerOutput'), top=boxBarCont.height + 23)
        self.upgradePowerGauge.ShowMarker(value=powerValue, color=util.Color.GetGrayRGBA(0.0, 0.5))
        self.costText = planet.ui.CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/Common/Cost'), subtext=localization.GetByLabel('UI/PI/Common/NoCost'), top=boxBarCont.height + 65)
        cpuValue = float(self.currCPUOutput) / self.maxCPUOutput
        self.upgradeCPUGauge = uicls.GaugeMultiValue(parent=cont, colors=[planetCommon.PLANET_COLOR_CPU, planetCommon.PLANET_COLOR_CPUUPGRADE], values=[cpuValue, 0.0], label=localization.GetByLabel('UI/PI/Common/CpuOutput'), left=self.infoContRightColAt, top=boxBarCont.height + 23)
        self.upgradeCPUGauge.ShowMarker(value=cpuValue, color=util.Color.GetGrayRGBA(0.0, 0.5))
        btns = [(localization.GetByLabel('UI/PI/Common/Upgrade'), self._ApplyUpgrade, None)]
        btnGroup = uicls.ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
        self.upgradeButton = btnGroup.GetBtnByLabel(localization.GetByLabel('UI/PI/Common/Upgrade'))
        self.upgradeButton.Disable()
        return cont

    def OnUpgradeBarValueChanged(self, oldValue, newValue):
        self.newLevel = newValue
        txt = localization.GetByLabel('UI/PI/Common/UpgradeFromLevelXToY', currLevel=util.IntToRoman(self.currLevel + 1), newLevel=util.IntToRoman(self.newLevel + 1))
        skill = sm.GetService('skills').GetMySkillsFromTypeID(const.typeCommandCenterUpgrade)
        commandCenterSkillLevel = 0
        if skill is not None:
            commandCenterSkillLevel = skill.skillLevel
        if commandCenterSkillLevel < newValue:
            skillType = cfg.invtypes.Get(const.typeCommandCenterUpgrade)
            hint = localization.GetByLabel('UI/PI/Common/NeedSkillToUpgrade', skillLevel=util.IntToRoman(newValue), skillName=skillType.typeName)
            txt = localization.GetByLabel('UI/PI/Common/InsufficientSkillForUpgrade')
            self.upgradeButton.Disable()
        else:
            hint = ''
            self.upgradeButton.Enable()
        self.upgradeText.SetCaption(txt)
        self.upgradeText.hint = hint
        newPowerOutput = planetCommon.GetPowerOutput(self.newLevel)
        self.upgradePowerGauge.SetValue(gaugeNum=1, value=newPowerOutput / self.maxPowerOutput)
        self.upgradePowerGauge.hint = self._GetPowerGaugeHint(newPowerOutput)
        self._SetPowerGaugeSubText(newPowerOutput)
        newCPUOutput = planetCommon.GetCPUOutput(self.newLevel)
        self.upgradeCPUGauge.SetValue(gaugeNum=1, value=newCPUOutput / self.maxCPUOutput)
        self.upgradeCPUGauge.hint = self._GetCPUGaugeHint(newCPUOutput)
        self._SetCPUGaugeSubText(newCPUOutput)
        iskCost = util.FmtISK(planetCommon.GetUpgradeCost(self.currLevel, self.newLevel), showFractionsAlways=0)
        self.costText.SetSubtext(iskCost)

    def _SetPowerGaugeSubText(self, newPowerOutput):
        diff = newPowerOutput - self.currPowerOutput
        subText = '+%s MW' % diff
        self.upgradePowerGauge.SetSubText(subText)

    def _GetPowerGaugeHint(self, newOutput):
        return localization.GetByLabel('UI/PI/Common/UpgradeHintPower', current=self.currPowerOutput, after=newOutput)

    def _GetCPUGaugeHint(self, newOutput):
        return localization.GetByLabel('UI/PI/Common/UpgradeHintCPU', current=self.currCPUOutput, after=newOutput)

    def _SetCPUGaugeSubText(self, newCPUOutput):
        diff = newCPUOutput - self.currCPUOutput
        subText = localization.GetByLabel('UI/PI/Common/CPUAdded', teraFlops=diff)
        self.upgradeCPUGauge.SetSubText(subText)

    def OnUpgradeBarBoxClicked(self, oldValue, newValue):
        return True

    def _ApplyUpgrade(self, *args):
        self.planetUISvc.planet.UpgradeCommandCenter(self.pin.id, self.newLevel)
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_upgrade_play')
        self.HideCurrentPanel()