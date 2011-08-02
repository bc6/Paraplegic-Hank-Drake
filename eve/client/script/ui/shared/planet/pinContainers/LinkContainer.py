import uix
import uiconst
import util
import planetCommon
import uicls
import planet
import const
import uiutil
import listentry

class LinkContainer(planet.ui.BasePinContainer):
    __guid__ = 'planet.ui.LinkContainer'
    default_name = 'LinkContainer'

    def _GetPinName(self):
        return cfg.invtypes.Get(self.pin.typeID).name



    def ApplyAttributes(self, attributes):
        planet.ui.BasePinContainer.ApplyAttributes(self, attributes)
        self.infoicon.state = uiconst.UI_HIDDEN



    def _GetActionButtons(self):
        btns = [util.KeyVal(name=mls.UI_PI_UPGRADELINK, panelCallback=self.PanelUpgrade, icon='ui_44_32_1'),
         util.KeyVal(name=mls.UI_PI_STATS, panelCallback=self.PanelShowStats, icon='ui_44_32_5'),
         util.KeyVal(name=mls.UI_PI_ROUTES, panelCallback=self.PanelShowRoutes, icon='ui_44_32_2'),
         util.KeyVal(name=mls.UI_PI_DECOMMISSION, panelCallback=self.PanelDecommissionLink, icon='ui_44_32_2')]
        return btns



    def PanelUpgrade(self):
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        link = self.pin.link
        infoSvc = sm.GetService('info')
        nextLevel = link.level + 1
        infoSvc = sm.GetService('info')
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
            text = mls.UI_PI_LINK_INSUFFICIENTCAPACITY % {'typeName': cfg.invtypes.Get(link.typeID).name}
            editBox = self._DrawEditBox(cont, text)
            self.upgradeStatsScroll = scroll = uicls.Scroll(parent=cont, name='upgradeStatsScroll', align=uiconst.TOTOP, height=58)
            self.upgradeStatsScroll.sr.id = 'planetLinkUpgradeStats'
            scroll.HideUnderLay()
            uicls.Frame(parent=scroll, color=(1.0, 1.0, 1.0, 0.2))
            scrolllist = []
            link = self.pin.link
            attr = cfg.dgmattribs.GetIfExists(const.attributeCpuLoad)
            strCurrentCpu = infoSvc.GetFormatAndValue(attr, currentCpu)
            strNextCpu = infoSvc.GetFormatAndValue(attr, nextLvlCpu)
            cpuDeficit = nextLvlCpu - (colonyCpuSupply - colonyCpuUsage)
            strCpuDeficit = infoSvc.GetFormatAndValue(attr, max(0, cpuDeficit))
            attr = cfg.dgmattribs.GetIfExists(const.attributeCpuLoad)
            strCurrentPower = infoSvc.GetFormatAndValue(attr, currentPower)
            strNextPower = infoSvc.GetFormatAndValue(attr, nextLvlPower)
            powerDeficit = nextLvlPower - (colonyPowerSupply - colonyPowerUsage)
            strPowerDeficit = infoSvc.GetFormatAndValue(attr, max(0, powerDeficit))
            if cpuDeficit > 0:
                strCpuDeficit = '<font color=red>' + strCpuDeficit + '</font>'
            else:
                strCpuDeficit = '<font color=green>' + strCpuDeficit + '</font>'
            if powerDeficit > 0:
                strPowerDeficit = '<font color=red>' + strPowerDeficit + '</font>'
            else:
                strPowerDeficit = '<font color=green>' + strPowerDeficit + '</font>'
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (mls.UI_PI_CPUUSAGE,
             strCurrentCpu,
             strNextCpu,
             strCpuDeficit))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (mls.UI_PI_POWERUSAGE,
             strCurrentPower,
             strNextPower,
             strPowerDeficit))
            scrolllist.append(listentry.Get('Generic', data=data))
            scroll.Load(contentList=scrolllist, headers=['',
             mls.UI_GENERIC_CURRENT,
             mls.UI_PI_UPGRADE,
             mls.UI_GENERIC_DEFICIT])
            cont.height = editBox.height + 58
        elif nextLevel > planetCommon.LINK_MAX_UPGRADE:
            text = mls.UI_PI_LINK_MAXIMUMUPGRADE % {'typeName': cfg.invtypes.Get(link.typeID).name}
            editBox = self._DrawEditBox(cont, text)
            cont.height = editBox.height
        else:
            text = mls.UI_PI_LINKUPGRADE2 % {'level': nextLevel}
            self.upgradeStatsScroll = scroll = uicls.Scroll(parent=cont, name='UpgradeStatsScroll', align=uiconst.TOTOP, height=96)
            self.upgradeStatsScroll.sr.id = 'planetLinkUpgradeStats'
            scroll.HideUnderLay()
            uicls.Frame(parent=scroll, color=(1.0, 1.0, 1.0, 0.2))
            scrolllist = []
            link = self.pin.link
            totalBandwidth = link.GetTotalBandwidth()
            nextLvlBandwidth = link.GetBandwidthForLevel(nextLevel)
            attr = cfg.dgmattribs.GetIfExists(const.attributeLogisticalCapacity)
            strCurrentBandwidth = totalBandwidth
            strNextLvlBandwidth = nextLvlBandwidth
            strBandwidthDelta = max(0, nextLvlBandwidth - totalBandwidth)
            strBandwidthUsage = link.GetBandwidthUsage()
            attr = cfg.dgmattribs.GetIfExists(const.attributeCpuLoad)
            strCurrentCpu = infoSvc.GetFormatAndValue(attr, currentCpu)
            strNextCpu = infoSvc.GetFormatAndValue(attr, nextLvlCpu)
            strCpuDelta = infoSvc.GetFormatAndValue(attr, max(0, nextLvlCpu - currentCpu))
            strCpuUsage = infoSvc.GetFormatAndValue(attr, colonyCpuUsage)
            attr = cfg.dgmattribs.GetIfExists(const.attributePowerLoad)
            strCurrentPower = infoSvc.GetFormatAndValue(attr, currentPower)
            strNextPower = infoSvc.GetFormatAndValue(attr, nextLvlPower)
            strPowerDelta = infoSvc.GetFormatAndValue(attr, max(0, nextLvlPower - currentPower))
            strPowerUsage = infoSvc.GetFormatAndValue(attr, colonyPowerUsage)
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (mls.UI_GENERIC_CURRENT,
             strCurrentBandwidth,
             strCurrentCpu,
             strCurrentPower))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (mls.UI_PI_UPGRADE,
             strNextLvlBandwidth,
             strNextCpu,
             strNextPower))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (mls.UI_GENERIC_CHANGE,
             strBandwidthDelta,
             strCpuDelta,
             strPowerDelta))
            scrolllist.append(listentry.Get('Generic', data=data))
            data = util.KeyVal(label='%s<t>%s<t>%s<t>%s' % (mls.UI_GENERIC_USAGE,
             strBandwidthUsage,
             strCpuUsage,
             strPowerUsage))
            scrolllist.append(listentry.Get('Generic', data=data))
            scroll.Load(contentList=scrolllist, headers=['',
             mls.UI_GENERIC_CAPACITY,
             mls.UI_GENERIC_CPU,
             mls.UI_GENERIC_POWER])
            btns = [[mls.UI_PI_UPGRADE, self._UpgradeSelf, (link.endpoint1.id, link.endpoint2.id, nextLevel)]]
            uicls.ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
            editBox = self._DrawEditBox(cont, text)
            cont.height = editBox.height + 115
        return cont



    def PanelDecommissionLink(self):
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 0), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        text = mls.UI_PI_LINK_DECOMMISSION_PROMPT % {'typeName': cfg.invtypes.Get(self.pin.link.typeID).name}
        editBox = self._DrawEditBox(cont, text)
        cont.height = editBox.height + 25
        btns = [[mls.UI_GENERIC_PROCEED, self._DecommissionSelf, None]]
        uicls.ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
        return cont



    def LoadRouteScroll(self):
        if not self or self.destroyed:
            return 
        link = self.pin.link
        scrolllist = []
        infoSvc = sm.GetService('info')
        bandwidthAttr = cfg.dgmattribs.Get(const.attributeLogisticalCapacity)
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(link.endpoint1.ownerID)
        for routeID in link.routesTransiting:
            route = colony.GetRoute(routeID)
            typeID = route.GetType()
            qty = route.GetQuantity()
            typeName = cfg.invtypes.Get(typeID).typeName
            data = util.KeyVal(label='<t>%s<t>%s<t>%s' % (typeName, qty, infoSvc.GetFormatAndValue(bandwidthAttr, route.GetBandwidthUsage())), typeID=typeID, itemID=None, getIcon=True, OnMouseEnter=self.OnRouteEntryHover, OnMouseExit=self.OnRouteEntryExit, routeID=route.routeID, OnClick=self.OnRouteEntryClick)
            scrolllist.append(listentry.Get('Item', data=data))

        self.routeScroll.Load(contentList=scrolllist, noContentHint=mls.UI_PI_NOROUTES, headers=['',
         mls.UI_GENERIC_COMMODITY,
         mls.UI_GENERIC_QUANTITY,
         mls.UI_GENERIC_LOAD])



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
        self.routeInfoType.SetSubtext(mls.UI_PI_UNITSOFTYPE % {'typeName': cfg.invtypes.Get(routeTypeID).name,
         'quantity': routeQty})
        bandwidthAttr = cfg.dgmattribs.Get(const.attributeLogisticalCapacity)
        infoSvc = sm.GetService('info')
        self.routeInfoBandwidth.SetSubtext(infoSvc.GetFormatAndValue(bandwidthAttr, selectedRoute.GetBandwidthUsage()))
        self.routeInfo.opacity = 0.0
        self.routeInfo.state = uiconst.UI_PICKCHILDREN
        self.showRoutesCont.height = 168 + self.routeInfo.height
        self.ResizeActionCont(self.showRoutesCont.height)
        self.uiEffects.MorphUI(self.routeInfo, 'opacity', 1.0, time=125.0, float=1, newthread=0, maxSteps=1000)



    def GetCaptionForUpgradeLevel(self, level):
        if level >= planetCommon.LINK_MAX_UPGRADE:
            return mls.UI_PI_GENERIC_EXPERIMENTAL
        else:
            if level == 9:
                return mls.UI_PI_GENERIC_STATEOFTHEART
            if level == 8:
                return mls.UI_GENERIC_ADVANCED
            if level == 7:
                return mls.UI_PI_GENERIC_EXPRESS
            if level == 6:
                return mls.UI_PI_GENERIC_EXPEDITED
            if level == 5:
                return mls.UI_GENERIC_FAST
            if level == 4:
                return mls.UI_SHARED_CERTGRADE3
            if level == 3:
                return mls.UI_GENERIC_STANDARD
            if level == 2:
                return mls.UI_GENERIC_BASIC
            if level == 1:
                return mls.UI_GENERIC_LOCAL
            return mls.UI_GENERIC_NONE



    def _DecommissionSelf(self, *args):
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_decommission_play')
        print 'LinkContainer::DecommissionSelf',
        print self.pin.GetIDTuple()
        self.planetUISvc.myPinManager.RemoveLink(self.pin.GetIDTuple())
        self.CloseX()



    def _UpgradeSelf(self, *args):
        self.planetUISvc.myPinManager.UpgradeLink(*args)
        self.CloseX()



    def _GetInfoCont(self):
        p = self.infoContPad
        infoCont = self._DrawAlignTopCont(55, 'infoCont', padding=(p,
         p,
         p,
         p))
        link = self.pin.link
        infoSvc = sm.GetService('info')
        attr = cfg.dgmattribs.GetIfExists(const.attributeLogisticalCapacity)
        totalBandwidth = infoSvc.GetFormatAndValue(attr, link.GetTotalBandwidth())
        bandwidthUsed = infoSvc.GetFormatAndValue(attr, link.GetBandwidthUsage())
        self.totalBandwidth = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_LOGISTICALCAPACITY, subtext=totalBandwidth)
        self.bandwidthUsed = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.UI_PI_CAPACITYUSED, subtext=bandwidthUsed, top=30)
        levelStr = '%s - %s' % (uiutil.IntToRoman(link.level), self.GetCaptionForUpgradeLevel(link.level)) if link.level > 0 else self.GetCaptionForUpgradeLevel(link.level)
        left = self.infoContRightColAt
        self.bandwidthGauge = uicls.Gauge(parent=infoCont, value=link.GetBandwidthUsage() / link.GetTotalBandwidth(), color=planetCommon.PLANET_COLOR_BANDWIDTH, label=mls.UI_PI_CAPACITYUSED, left=left)
        self.upgradeLevel = planet.ui.CaptionAndSubtext(parent=infoCont, caption=mls.STATION_UPGRADE_LEVEL, subtext=levelStr, top=30, left=left)
        return infoCont



    def _UpdateInfoCont(self):
        if not self or self.destroyed:
            return 
        link = self.pin.link
        infoSvc = sm.GetService('info')
        attr = cfg.dgmattribs.GetIfExists(const.attributeLogisticalCapacity)
        totalBandwidth = infoSvc.GetFormatAndValue(attr, link.GetTotalBandwidth())
        bandwidthUsed = infoSvc.GetFormatAndValue(attr, link.GetBandwidthUsage())
        self.totalBandwidth.SetSubtext(totalBandwidth)
        self.bandwidthUsed.SetSubtext(bandwidthUsed)
        levelStr = '%s - %s' % (uiutil.IntToRoman(link.level), self.GetCaptionForUpgradeLevel(link.level)) if link.level > 0 else self.GetCaptionForUpgradeLevel(link.level)
        self.upgradeLevel.SetSubtext(levelStr)
        self.bandwidthGauge.SetValue(link.GetBandwidthUsage() / link.GetTotalBandwidth())



    def PanelShowStats(self, *args):
        cont = uicls.Container(parent=self.actionCont, pos=(0, 0, 0, 175), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        self.statsScroll = scroll = uicls.Scroll(parent=cont, name='StatsScroll', align=uiconst.TOTOP, height=170)
        scroll.HideUnderLay()
        uicls.Frame(parent=scroll, color=(1.0, 1.0, 1.0, 0.2))
        scrolllist = []
        link = self.pin.link
        data = util.KeyVal(label='%s<t>%s %s' % (mls.UI_PI_CPUUSAGE, link.GetCpuUsage(), mls.UI_GENERIC_TERAFLOPSSHORT))
        scrolllist.append(listentry.Get('Generic', data=data))
        data = util.KeyVal(label='%s<t>%s %s' % (mls.UI_PI_POWERUSAGE, link.GetPowerUsage(), mls.UI_GENERIC_MEGAWATTSHORT))
        scrolllist.append(listentry.Get('Generic', data=data))
        scroll.Load(contentList=scrolllist, headers=[mls.UI_CHARCREA_ATTRIBUTE, mls.UI_GENERIC_VALUE])
        return cont




