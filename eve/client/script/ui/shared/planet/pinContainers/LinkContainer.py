import uix
import uiconst
import util
import planetCommon
import uicls
import planet
import const
import uiutil
import listentry
import localization
import localizationUtil

class LinkContainer(planet.ui.BasePinContainer):
    __guid__ = 'planet.ui.LinkContainer'
    default_name = 'LinkContainer'

    def _GetPinName(self):
        return cfg.invtypes.Get(self.pin.typeID).name



    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)
        self.infoicon.state = uiconst.UI_HIDDEN



    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommon.PANEL_UPGRADELINK, panelCallback=self.PanelUpgrade),
         util.KeyVal(id=planetCommon.PANEL_STATS, panelCallback=self.PanelShowStats),
         util.KeyVal(id=planetCommon.PANEL_ROUTES, panelCallback=self.PanelShowRoutes),
         util.KeyVal(id=planetCommon.PANEL_DECOMMISSION, panelCallback=self.PanelDecommissionLink)]
        return btns



    def PanelUpgrade(self):
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        link = self.pin.link
        nextLevel = link.level + 1
        currentCpu = link.GetCpuUsage()
        currentPower = link.GetPowerUsage()
        nextLvlCpu = planetCommon.GetCpuUsageForLink(link.typeID, link.GetDistance(), nextLevel)
        nextLvlPower = planetCommon.GetPowerUsageForLink(link.typeID, link.GetDistance(), nextLevel)
        addlCpu = max(0, nextLvlCpu - currentCpu)
        addlPower = max(0, nextLvlPower - currentPower)
        colony = self.planetUISvc.GetCurrentPlanet().GetColony(session.charid)
        if not colony or colony.colonyData is None:
            raise RuntimeError('Unable to upgrade link - colony not set up')
        colonyCpuUsage = colony.colonyData.GetColonyCpuUsage()
        colonyCpuSupply = colony.colonyData.GetColonyCpuSupply()
        colonyPowerUsage = colony.colonyData.GetColonyPowerUsage()
        colonyPowerSupply = colony.colonyData.GetColonyPowerSupply()
        if addlPower + colonyPowerUsage > colonyPowerSupply or addlCpu + colonyCpuUsage > colonyCpuSupply:
            text = localization.GetByLabel('UI/PI/Common/LinkCannotUpgradePowerCPU', linkTypeName=cfg.invtypes.Get(link.typeID).name)
            editBox = self._DrawEditBox(cont, text)
            self.upgradeStatsScroll = scroll = uicls.Scroll(parent=cont, name='upgradeStatsScroll', align=uiconst.TOTOP, height=58)
            self.upgradeStatsScroll.sr.id = 'planetLinkUpgradeStats'
            scroll.HideUnderLay()
            uicls.Frame(parent=scroll, color=(1.0, 1.0, 1.0, 0.2))
            scrolllist = []
            link = self.pin.link
            strCurrentCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=currentCpu)
            strNextCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=nextLvlCpu)
            cpuDeficit = nextLvlCpu - (colonyCpuSupply - colonyCpuUsage)
            if cpuDeficit > 0:
                cerberusLabel = 'UI/PI/Common/TeraFlopsAmountRed'
            else:
                cerberusLabel = 'UI/PI/Common/TeraFlopsAmountGreen'
            strCpuDeficit = localization.GetByLabel(cerberusLabel, amount=max(0, cpuDeficit))
            strCurrentPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=currentPower)
            strNextPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=nextLvlPower)
            powerDeficit = nextLvlPower - (colonyPowerSupply - colonyPowerUsage)
            if powerDeficit > 0:
                cerberusLabel = 'UI/PI/Common/MegaWattsAmountRed'
            else:
                cerberusLabel = 'UI/PI/Common/MegaWattsAmountGreen'
            strPowerDeficit = localization.GetByLabel(cerberusLabel, amount=max(0, powerDeficit))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuUsage'),
             strCurrentCpu,
             strNextCpu,
             strCpuDeficit))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerUsage'),
             strCurrentPower,
             strNextPower,
             strPowerDeficit))
            scrolllist.append(listentry.Get('Generic', data=data))
            scroll.Load(contentList=scrolllist, headers=['',
             localization.GetByLabel('UI/Common/Current'),
             localization.GetByLabel('UI/PI/Common/UpgradeNoun'),
             localization.GetByLabel('UI/PI/Common/PowerOrCPUDeficit')])
            cont.height = editBox.height + 58
        elif nextLevel > planetCommon.LINK_MAX_UPGRADE:
            text = localization.GetByLabel('UI/PI/Common/LinkMaxUpgradeReached', linkTypeName=cfg.invtypes.Get(link.typeID).name)
            editBox = self._DrawEditBox(cont, text)
            cont.height = editBox.height
        else:
            text = localization.GetByLabel('UI/PI/Common/LinkUpgradePrompt', level=nextLevel)
            self.upgradeStatsScroll = scroll = uicls.Scroll(parent=cont, name='UpgradeStatsScroll', align=uiconst.TOTOP, height=96)
            self.upgradeStatsScroll.sr.id = 'planetLinkUpgradeStats'
            scroll.HideUnderLay()
            uicls.Frame(parent=scroll, color=(1.0, 1.0, 1.0, 0.2))
            scrolllist = []
            link = self.pin.link
            totalBandwidth = link.GetTotalBandwidth()
            nextLvlBandwidth = link.GetBandwidthForLevel(nextLevel)
            strCurrentBandwidth = totalBandwidth
            strNextLvlBandwidth = nextLvlBandwidth
            strBandwidthDelta = max(0, nextLvlBandwidth - totalBandwidth)
            strBandwidthUsage = link.GetBandwidthUsage()
            strCurrentCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=currentCpu)
            strNextCpu = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=nextLvlCpu)
            strCpuDelta = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=max(0, nextLvlCpu - currentCpu))
            strCpuUsage = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=int(colonyCpuUsage))
            strCurrentPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=currentPower)
            strNextPower = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=nextLvlPower)
            strPowerDelta = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=max(0, nextLvlPower - currentPower))
            strPowerUsage = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=int(colonyPowerUsage))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/Common/Current'),
             localizationUtil.FormatNumeric(strCurrentBandwidth, decimalPlaces=1),
             strCurrentCpu,
             strCurrentPower))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/UpgradeNoun'),
             localizationUtil.FormatNumeric(strNextLvlBandwidth, decimalPlaces=1),
             strNextCpu,
             strNextPower))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/PI/Common/ChangeNoun'),
             localizationUtil.FormatNumeric(strBandwidthDelta, decimalPlaces=1),
             strCpuDelta,
             strPowerDelta))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (localization.GetByLabel('UI/Common/Usage'),
             localizationUtil.FormatNumeric(strBandwidthUsage, decimalPlaces=1),
             strCpuUsage,
             strPowerUsage))
            scrolllist.append(listentry.Get('Generic', data=data))
            scroll.Load(contentList=scrolllist, headers=['',
             localization.GetByLabel('UI/PI/Common/Capacity'),
             localization.GetByLabel('UI/Common/Cpu'),
             localization.GetByLabel('UI/Common/Power')])
            btns = [[localization.GetByLabel('UI/PI/Common/Upgrade'), self._UpgradeSelf, (link.endpoint1.id, link.endpoint2.id, nextLevel)]]
            uicls.ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
            editBox = self._DrawEditBox(cont, text)
            cont.height = editBox.height + 115
        return cont



    def PanelDecommissionLink(self):
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        text = localization.GetByLabel('UI/PI/Common/DecommissionLink', typeName=cfg.invtypes.Get(self.pin.link.typeID).name)
        editBox = self._DrawEditBox(cont, text)
        cont.height = editBox.height + 25
        btns = [[localization.GetByLabel('UI/PI/Common/Proceed'), self._DecommissionSelf, None]]
        uicls.ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
        return cont



    def LoadRouteScroll(self):
        if not self or self.destroyed:
            return 
        link = self.pin.link
        scrolllist = []
        bandwidthAttr = cfg.dgmattribs.Get(const.attributeLogisticalCapacity)
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(link.endpoint1.ownerID)
        for routeID in link.routesTransiting:
            route = colony.GetRoute(routeID)
            typeID = route.GetType()
            qty = route.GetQuantity()
            typeName = cfg.invtypes.Get(typeID).typeName
            data = util.KeyVal(label='<t>%s<t>%s<t>%s' % (typeName, qty, localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=route.GetBandwidthUsage())), typeID=typeID, itemID=None, getIcon=True, OnMouseEnter=self.OnRouteEntryHover, OnMouseExit=self.OnRouteEntryExit, routeID=route.routeID, OnClick=self.OnRouteEntryClick)
            scrolllist.append(listentry.Get('Item', data=data))

        self.routeScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoRoutesThroughLink'), headers=['',
         localization.GetByLabel('UI/Common/Commodity'),
         localization.GetByLabel('UI/Common/Quantity'),
         localization.GetByLabel('UI/PI/Common/CapacityUsed')])



    def OnRouteEntryHover(self, entry):
        self.planetUISvc.myPinManager.ShowRoute(entry.sr.node.routeID)



    def OnRouteEntryExit(self, entry):
        self.planetUISvc.myPinManager.StopShowingRoute(entry.sr.node.routeID)



    def OnRouteEntryClick(self, *args):
        if not self or self.destroyed:
            return 
        selectedRoutes = self.routeScroll.GetSelected()
        if len(selectedRoutes) < 1:
            self.routeInfo.state = uiconst.UI_HIDDEN
            self.showRoutesCont.height = 168
            self.ResizeActionCont(self.showRoutesCont.height)
            return 
        selectedRouteData = selectedRoutes[0]
        selectedRouteID = None
        for routeID in self.pin.link.routesTransiting:
            if routeID == selectedRouteData.routeID:
                selectedRouteID = routeID
                break

        if selectedRouteID is None:
            return 
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(self.pin.link.endpoint1.ownerID)
        selectedRoute = colony.GetRoute(selectedRouteID)
        if selectedRoute is None:
            return 
        sourcePin = colony.GetPin(selectedRoute.GetSourcePinID())
        self.routeInfoSource.SetSubtext(planetCommon.GetGenericPinName(sourcePin.typeID, sourcePin.id))
        destPin = colony.GetPin(selectedRoute.GetDestinationPinID())
        self.routeInfoDest.SetSubtext(planetCommon.GetGenericPinName(destPin.typeID, destPin.id))
        routeTypeID = selectedRoute.GetType()
        routeQty = selectedRoute.GetQuantity()
        self.routeInfoType.SetSubtext(localization.GetByLabel('UI/PI/Common/ItemAmount', itemName=cfg.invtypes.Get(routeTypeID).name, amount=int(routeQty)))
        bandwidthAttr = cfg.dgmattribs.Get(const.attributeLogisticalCapacity)
        self.routeInfoBandwidth.SetSubtext(localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=selectedRoute.GetBandwidthUsage()))
        self.routeInfo.opacity = 0.0
        self.routeInfo.state = uiconst.UI_PICKCHILDREN
        self.showRoutesCont.height = 168 + self.routeInfo.height
        self.ResizeActionCont(self.showRoutesCont.height)
        self.uiEffects.MorphUI(self.routeInfo, 'opacity', 1.0, time=125.0, float=1, newthread=0, maxSteps=1000)



    def GetCaptionForUpgradeLevel(self, level):
        if level >= planetCommon.LINK_MAX_UPGRADE:
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel10')
        else:
            if level == 9:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel9')
            if level == 8:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel8')
            if level == 7:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel7')
            if level == 6:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel6')
            if level == 5:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel5')
            if level == 4:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel4')
            if level == 3:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel3')
            if level == 2:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel2')
            if level == 1:
                return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel1')
            return localization.GetByLabel('UI/PI/Common/LinkUpgradeLevel0')



    def _DecommissionSelf(self, *args):
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_decommission_play')
        self.planetUISvc.myPinManager.RemoveLink(self.pin.GetIDTuple())
        self.CloseByUser()



    def _UpgradeSelf(self, *args):
        self.planetUISvc.myPinManager.UpgradeLink(*args)
        self.CloseByUser()



    def _GetInfoCont(self):
        p = self.infoContPad
        infoCont = self._DrawAlignTopCont(55, 'infoCont', padding=(p,
         p,
         p,
         p))
        link = self.pin.link
        totalBandwidth = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetTotalBandwidth())
        bandwidthUsed = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetBandwidthUsage())
        self.totalBandwidth = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/LinkMaxCapacity'), subtext=totalBandwidth)
        self.bandwidthUsed = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/CapacityUsed'), subtext=bandwidthUsed, top=30)
        left = self.infoContRightColAt
        self.bandwidthGauge = uicls.Gauge(parent=infoCont, value=link.GetBandwidthUsage() / link.GetTotalBandwidth(), color=planetCommon.PLANET_COLOR_BANDWIDTH, label=localization.GetByLabel('UI/PI/Common/CapacityUsed'), left=left)
        levelStr = localization.GetByLabel('UI/PI/Common/LinkUpgradeLevelAndName', upgradeLevel=uiutil.IntToRoman(link.level), upgradeLevelName=self.GetCaptionForUpgradeLevel(link.level))
        self.upgradeLevel = planet.ui.CaptionAndSubtext(parent=infoCont, caption=localization.GetByLabel('UI/PI/Common/UpgradeLevel'), subtext=levelStr, top=30, left=left)
        return infoCont



    def _UpdateInfoCont(self):
        if not self or self.destroyed:
            return 
        link = self.pin.link
        totalBandwidth = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetTotalBandwidth())
        bandwidthUsed = localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=link.GetBandwidthUsage())
        self.totalBandwidth.SetSubtext(totalBandwidth)
        self.bandwidthUsed.SetSubtext(bandwidthUsed)
        levelStr = localization.GetByLabel('UI/PI/Common/LinkUpgradeLevelAndName', upgradeLevel=uiutil.IntToRoman(link.level), upgradeLevelName=self.GetCaptionForUpgradeLevel(link.level))
        self.upgradeLevel.SetSubtext(levelStr)
        self.bandwidthGauge.SetValue(link.GetBandwidthUsage() / link.GetTotalBandwidth())



    def PanelShowStats(self, *args):
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 175), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        self.statsScroll = scroll = uicls.Scroll(parent=cont, name='StatsScroll', align=uiconst.TOTOP, height=170)
        scroll.HideUnderLay()
        uicls.Frame(parent=scroll, color=(1.0, 1.0, 1.0, 0.2))
        scrolllist = []
        link = self.pin.link
        strCpuUsage = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=int(link.GetCpuUsage()))
        data = util.KeyVal(label='%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuUsage'), strCpuUsage))
        scrolllist.append(listentry.Get('Generic', data=data))
        strPowerUsage = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=int(link.GetPowerUsage()))
        data = util.KeyVal(label='%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerUsage'), strPowerUsage))
        scrolllist.append(listentry.Get('Generic', data=data))
        scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/PI/Common/Attribute'), localization.GetByLabel('UI/Common/Value')])
        return cont




