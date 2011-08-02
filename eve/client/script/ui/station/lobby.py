import base
import blue
import form
import listentry
import log
import sys
import uix
import uiutil
import uthread
import util
import uicls
import uiconst
import xtriui
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L
MAX_CORP_DESC_LENGTH = 140
MAX_CORP_DESC_LINES = 1

def MakeURLTag(url):
    if url.find('.') < 0:
        return url
    _url = url
    if _url.find('://') < 0:
        _url = 'http://' + url
    return '<url=%(_url)s>%(url)s</url>' % {'_url': _url,
     'url': url}



def CutAtLength(l, txt):
    if txt == None or len(txt) <= l:
        return txt
    else:
        return txt[:(l - 3)] + '...'



def CutAtLines(nlines, txt):
    if txt.count('<br>') < nlines:
        return txt
    else:
        i = 0
        numFnd = 0
        while numFnd < MAX_CORP_DESC_LINES:
            i = txt.find('<br>', i + 1)
            numFnd += 1

        return txt[:i] + '...'



class Lobby(uicls.Window):
    __guid__ = 'form.Lobby'
    __notifyevents__ = ['OnCharNowInStation',
     'OnCharNoLongerInStation',
     'OnProcessStationServiceItemChange',
     'OnAgentMissionChange',
     'OnStandingSet',
     'OnCorporationChanged',
     'OnCorporationMemberChanged']
    default_left = '__right__'
    default_top = 0

    def default_height(self):
        return uicore.desktop.height - 305



    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.registeredMacho = 0
        self.sr.scroll = None
        self.sr.lobbytabs = None
        self.DoReset()
        self.sr.serviceAccessCache = {}
        self.isWindow = 1
        self.locationparentheight = 0
        self.btnparentheight = 0
        self.startedUp = 0
        uiutil.Flush(uicore.layer.menu)
        self.SetWndIcon(None)
        self.SetMinSize([238 if settings.user.ui.Get('stationservicebtns', 0) else 270, 463])
        self.SetCaption(mls.UI_STATION_STSERVICES)
        self.scope = 'station'
        self.MakeUnKillable()
        self.MakeUnstackable()
        self.SetTopparentHeight(0)
        main = self.sr.main
        self.sr.buttonParent = buttonParent = uicls.Container(name='buttonParent', align=uiconst.TOBOTTOM, height=0, parent=main)
        self.sr.btnparent = btnparent = uicls.Container(name='btnparent', align=uiconst.TOTOP, width=0, height=128, parent=main)
        self.sr.bottomparent = bottomparent = uicls.Container(name='bottomparent', align=uiconst.TOALL, parent=main, pos=(0, 0, 0, 0))
        self.agentFinderCont = uicls.Container(name='agentFinderCont', parent=bottomparent, align=uiconst.TOTOP, height=20, state=uiconst.UI_HIDDEN)
        self.agentFinderBtn = uicls.Button(label=mls.UI_SHARED_AGENTFINDER, parent=self.agentFinderCont, align=uiconst.TOTOP, height=20, func=uicore.cmd.OpenAgentFinder, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        lobbyscroll = uicls.Scroll(parent=bottomparent)
        lobbyscroll.left = lobbyscroll.top = lobbyscroll.width = lobbyscroll.height = const.defaultPadding
        self.sr.scroll = lobbyscroll
        tabs = [[mls.UI_GENERIC_GUESTS,
          lobbyscroll,
          self,
          'lobby_guests'], [mls.UI_GENERIC_AGENTS,
          lobbyscroll,
          self,
          'lobby_agents'], [mls.UI_CORP_OFFICES,
          lobbyscroll,
          self,
          'lobby_offices']]
        self.sr.lobbytabs = uicls.TabGroup(name='tabparent', parent=bottomparent, idx=0)
        self.sr.lobbytabs.Startup(tabs, 'lobbytabs', autoselecttab=0, UIIDPrefix='stationInformationTab')
        if eve.rookieState is None and settings.user.windows.Get('dockshipsanditems', 0):
            self.sr.shipsContainer = xtriui.DropDude(parent=bottomparent, state=uiconst.UI_HIDDEN)
            self.sr.itemsContainer = xtriui.DropDude(parent=bottomparent, state=uiconst.UI_HIDDEN)
            tabs = [[mls.UI_GENERIC_SHIPS,
              self.sr.shipsContainer,
              self,
              'lobby_ships'], [mls.UI_GENERIC_ITEMS,
              self.sr.itemsContainer,
              self,
              'lobby_items']]
            lobbytabs = uicls.TabGroup(name='tabparent', parent=bottomparent, idx=1)
            lobbytabs.Startup(tabs, 'lobbytabs', autoselecttab=0)
            self.sr.lobbytabs.AddRow(lobbytabs)
        uthread.pool('lobby::_Startup', self.sr.lobbytabs.AutoSelect, 1)
        self.LoadServiceButtons()
        uthread.new(self.LoadButtons)
        sm.GetService('neocom').Position()
        sm.GetService('ui').SortGlobalLayer()
        if self.destroyed:
            return 
        sm.RegisterNotify(self)
        self.registeredMacho = 1
        self.startedUp = 1
        self.OnEndScale_()
        if settings.user.windows.Get('dockshipsanditems', 0):
            self.LayoutShipsAndItems()



    def LayoutShipsAndItems(self):
        wnd = sm.GetService('window').GetWindow('hangarFloor')
        if wnd:
            wnd.CloseX()
        wnd = form.ItemHangar(name='hangarFloor')
        self.ImplantWindow('items', wnd)
        wnd = sm.GetService('window').GetWindow('shipHangar')
        if wnd:
            wnd.CloseX()
        wnd = form.ShipHangar(name='shipHangar')
        self.ImplantWindow('ships', wnd)



    def OnClose_(self, *args):
        self.DoReset()



    def DoReset(self):
        if not self or self.destroyed:
            return 
        self.sr.mainparent = None
        if self.sr.lobbytabs is not None and not self.sr.lobbytabs.destroyed:
            self.sr.lobbytabs.Close()
        self.sr.lobbytabs = None
        if self.sr.scroll is not None and not self.sr.scroll.destroyed:
            self.sr.scroll.Close()
        self.sr.scroll = None
        self.sr.state = None
        for wndID in ('items', 'ships'):
            container = self.sr.Get('%sContainer' % wndID, None)
            if container is not None and len(container.children):
                container.children[0].Close()




    def ImplantWindow(self, wndID, wnd):
        uthread.new(self._ImplantWindow, wndID, wnd)



    def _ImplantWindow(self, wndID, wnd):
        if self.destroyed:
            return 
        container = self.sr.Get('%sContainer' % wndID, None)
        if container is None or container.destroyed or wnd is None or wnd.destroyed:
            return 
        if wnd.GetAlign() == uiconst.TOALL and wnd.parent == container:
            return 
        if wnd.sr.stack:
            wnd.sr.stack.RemoveWnd(wnd, [wnd.sr.stack.left, wnd.sr.stack.top])
        if len(container.children) and container.children[0] is not wnd:
            uix.Flush(container)
        if wnd is None or wnd.destroyed:
            return 
        wnd.HideHeader()
        wnd.MakeUnResizeable()
        if wndID in ('items', 'ships'):
            uiutil.GetChild(wnd, 'mainicon').top = -6
            uiutil.GetChild(wnd, 'text').top = 2
            wnd.sr.iconsModeBtn.top = 10
            wnd.sr.detailsModeBtn.top = 10
            wnd.sr.listModeBtn.top = 10
            wnd.SetTopparentHeight(32)
            wnd.MakeUnMinimizable()
            wnd.GetMenu = None
        else:
            uiutil.GetChild(wnd, 'mainicon').state = uiconst.UI_HIDDEN
            wnd.SetTopparentHeight(0)
        wnd.children[-1].state = uiconst.UI_HIDDEN
        wnd.canCloseActiveWnd = 0
        uiutil.Transplant(wnd, container)
        wnd.SetAlign(uiconst.TOALL)
        wnd.left = wnd.top = wnd.width = wnd.height = 0
        wnd.state = uiconst.UI_PICKCHILDREN
        wnd.sr.tab = container.sr.tab
        wnd.isImplanted = 1
        container.state = uiconst.UI_HIDDEN
        self.sr.lobbytabs.ShowPanel(container)
        if len(container.children) and container.children[0] == wnd:
            if container.state == uiconst.UI_HIDDEN and getattr(wnd.sr, 'tab', None) is not None and wnd.sr.tab.selecting == 0:
                self.sr.lobbytabs.ShowPanel(container)
        if hasattr(wnd, 'UpdateCaption'):
            wnd.UpdateCaption()



    def CloseDown(self):
        if self.registeredMacho:
            sm.UnregisterNotify(self)
            self.registeredMacho = 0



    def OnProcessStationServiceItemChange(self, stationID, solarSystemID, serviceID, stationServiceItemID, isEnabled):
        if not util.GetAttrs(self, 'sr', 'btnparent', 'children'):
            return 
        if stationID != eve.session.stationid:
            return 
        for icon in self.sr.btnparent.children:
            if hasattr(icon, 'stationServiceIDs') and serviceID in icon.stationServiceIDs:
                self.SetServiceButtonState(icon, [serviceID])




    def OnAgentMissionChange(self, actionID, agentID, tutorialID = None):
        if self.sr.state == 'lobby_agents':
            self.ShowAgents()



    def OnCorporationChanged(self, corpID, change):
        blue.pyos.synchro.Yield()
        self.LoadButtons()



    def OnStandingSet(self, fromID, toID, rank):
        if self.sr.state == 'lobby_agents':
            self.ShowAgents()



    def SetServiceButtonState(self, icon, serviceIDs):
        for serviceID in serviceIDs:
            currentstate = sm.GetService('station').GetServiceState(serviceID)
            if currentstate is not None:
                if self.sr.serviceAccessCache.has_key(serviceID):
                    del self.sr.serviceAccessCache[serviceID]
                icn = uiutil.GetChild(icon, 'icon')
                if not currentstate.isEnabled:
                    icn.color.a = 0.5
                    icon.serviceStatus = mls.UI_SHARED_DISABLED
                else:
                    icn.color.a = 1.0
                    icon.serviceStatus = mls.UI_SHARED_ENABLED




    def LoadServiceButtons(self):
        parent = self.sr.btnparent
        uix.Flush(parent)
        services = sm.GetService('station').GetStationServiceInfo()
        serviceMask = eve.stationItem.serviceMask
        x = 0
        y = 0
        icon = None
        (l, t, w, h,) = parent.GetAbsolute()
        stationservicebtns = settings.user.ui.Get('stationservicebtns', 0)
        btnsize = 64
        if stationservicebtns:
            btnsize = 51
        haveServices = []
        for (serviceID, cmdStr, displayName, iconpath, stationOnly, stationServiceIDs,) in services:
            hasStationService = 0
            for stationServiceID in stationServiceIDs:
                if serviceMask & stationServiceID == stationServiceID:
                    if serviceID == 'navyoffices':
                        check = sm.StartService('facwar').CheckStationElegibleForMilitia()
                        if not check:
                            hasStationService = 0
                            break
                    hasStationService = 1
                    break

            if 1 == hasStationService or -1 in stationServiceIDs:
                haveServices.append((serviceID,
                 displayName,
                 iconpath,
                 stationServiceIDs,
                 1,
                 cmdStr))

        amountOfButtonsPerRow = w / btnsize
        amountOfButtonsPerRow = min(amountOfButtonsPerRow, len(haveServices))
        for (serviceID, displayName, iconpath, stationServiceIDs, hasStationService, cmdStr,) in haveServices:
            icon = uix.GetBigButton(btnsize, parent, left=0, top=0)
            icon.name = serviceID
            icon.cmdStr = cmdStr
            icon.stationServiceIDs = stationServiceIDs
            icon.displayName = displayName
            icon.OnClick = (self.OnSvcBtnClick, icon)
            icon.MouseEnter = self.OnSvcBtnMouseEnter
            icon.serviceStatus = mls.UI_SHARED_ENABLED
            icon.sr.icon.LoadIcon(iconpath)
            self.SetServiceButtonState(icon, stationServiceIDs)
            uiutil.SetOrder(icon, 0)

        self.LayoutServiceButtons()



    def OnSvcBtnMouseEnter(self, btn, *args):
        cmdshortcut = uicore.cmd.GetShortcutByString(btn.cmdStr)
        cmdshortcut = cmdshortcut or mls.UI_GENERIC_NONE
        btn.hint = mls.UI_SHARED_STATIONSERVICEBUTTONHINT % {'displayName': btn.displayName,
         'shortCut': '<b>%s</b>' % cmdshortcut,
         'serviceStatus': '<b>%s</b>' % btn.serviceStatus}
        btn.displayName + (' [%s]' % cmdshortcut, '')[(cmdshortcut is None)] + '<br>status: <b>%s</b>' % btn.serviceStatus



    def OnSvcBtnEnter(self, btn, *args):
        eve.Message('%sBtnEnter' % btn.name, ignoreNotFound=1)



    def OnSvcBtnClick(self, btn, *args):
        services = sm.GetService('station').GetStationServiceInfo()
        for (serviceID, cmdStr, displayName, iconpath, stationOnly, stationServiceIDs,) in services:
            if serviceID == btn.name:
                corpStationMgr = None
                now = blue.os.GetTime()
                for stationServiceID in stationServiceIDs:
                    doCheck = 1
                    (time, result,) = (None, None)
                    if self.sr.serviceAccessCache.has_key(stationServiceID):
                        (time, result,) = self.sr.serviceAccessCache[stationServiceID]
                        if time + MIN * 5 > now:
                            doCheck = 0
                    if doCheck:
                        if corpStationMgr is None:
                            corpStationMgr = sm.GetService('corp').GetCorpStationManager()
                        try:
                            corpStationMgr.DoStandingCheckForStationService(stationServiceID)
                            self.sr.serviceAccessCache[stationServiceID] = (now, None)
                        except Exception as e:
                            self.sr.serviceAccessCache[stationServiceID] = (now, e)
                            sys.exc_clear()
                    (time, result,) = self.sr.serviceAccessCache[stationServiceID]
                    if result is not None:
                        raise result


        sm.GetService('station').LoadSvc(btn.name)



    def LoadButtons(self):
        if not self or self.destroyed:
            return 
        uix.Flush(self.sr.buttonParent)
        btns = []
        self.sr.buttonParent.height = 0
        canRent = eve.session.corprole & const.corpRoleCanRentOffice == const.corpRoleCanRentOffice
        canMove = eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector
        deliveryRoles = const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader
        canOpenDeliveries = eve.session.corprole & deliveryRoles > 0
        if canRent:
            btns.append([mls.UI_CMD_RENTOFFICE, self.RentOffice, None])
        if canMove:
            btns.append([mls.UI_CMD_MOVEHQHERE, self.SetHQ, None])
        if not util.IsNPC(eve.session.corpid):
            btns.append([mls.UI_CMD_CORPHANGAR, self.OpenCorpHangar, None])
        if sm.GetService('corp').DoesCharactersCorpOwnThisStation():
            btns.append([mls.UI_CMD_STATIONMANAGEMENT, self.OpenStationManagement, None])
        if canOpenDeliveries:
            btns.append([mls.UI_CMD_DELIVERIES, uicore.cmd.OpenCorpDeliveries, (deliveryRoles,)])
        if self is None or self.destroyed:
            return 
        maxw = self.width - 12
        w = 0
        t = 0
        s = {}
        if btns != []:
            for (label, func, args,) in btns:
                btn = uicls.Button(parent=self.sr.buttonParent, label=label, func=func, args=args)
                if w + btn.width >= maxw:
                    t += btn.height + 6
                    w = 0
                btn.left = w
                btn.top = t
                w += btn.width + 4
                if btn.top not in s:
                    s[btn.top] = []
                s[btn.top].append(btn)

            for (top, btns,) in s.iteritems():
                totalw = sum([ btn.width for btn in btns ])
                diff = (self.width - totalw) / 2
                for btn in btns:
                    btn.left += diff


            self.sr.buttonParent.height = t + btn.height + 6



    def OpenCorpHangar(self, *args):
        if not self.sr.Get('isCorpHangarOpening') or not self.sr.isCorpHangarOpening:
            self.sr.isCorpHangarOpening = 1
            try:
                sm.GetService('window').OpenCorpHangar(None, None, 1)

            finally:
                self.sr.isCorpHangarOpening = 0




    def OpenStationManagement(self, *args):
        uthread.new(uicore.cmd.OpenStationManagement)



    def ImVisible(self):
        return bool(self.state != uiconst.UI_HIDDEN and not self.IsCollapsed() and not self.IsMinimized())



    def LayoutServiceButtons(self):
        if not self or self.destroyed:
            return 
        parent = self.sr.btnparent
        stationservicebtns = settings.user.ui.Get('stationservicebtns', 0)
        btnsize = 64
        if stationservicebtns:
            btnsize = 56
        (l, t, w, h,) = parent.GetAbsolute()
        if w <= btnsize:
            return 
        perRow = w / btnsize
        left = 4
        top = 4
        parent.height = btnsize + 8
        for icon in parent.children:
            if l + left + btnsize + 1 >= l + w:
                left = 4
                top += btnsize + 1
                parent.height += btnsize + 1
            icon.left = left
            icon.top = top
            icon.width = btnsize
            icon.height = btnsize
            if icon.state is not None:
                icon.state = uiconst.UI_NORMAL
            left += btnsize + 1
            icon.AdjustSizeAndPosition(btnsize, btnsize)




    def OnResize_(self, *args):
        if self and self.startedUp and not self.destroyed:
            self.sr.resizeTimer = base.AutoTimer(250, self.OnEndScale_)



    def OnEndScale_(self, *etc):
        self.sr.resizeTimer = None
        if self and self.startedUp and not self.destroyed:
            uthread.new(self.OnResizeDelayed)



    def OnResizeDelayed(self, *args):
        if not self or self.destroyed:
            return 
        self.LayoutServiceButtons()
        self.LoadButtons()



    def Load(self, key):
        if not self or self.destroyed:
            return 
        self.agentFinderCont.state = uiconst.UI_HIDDEN
        self.sr.state = key
        if key == 'lobby_guests':
            self.ShowGuests()
        elif key == 'lobby_agents':
            self.agentFinderCont.state = uiconst.UI_PICKCHILDREN
            self.ShowAgents()
        elif key == 'lobby_offices':
            self.ShowOffices()
        elif key == 'lobby_ships':
            pass
        elif key == 'lobby_items':
            pass



    def OnCharNowInStation(self, rec):
        (charID, corpID, allianceID, warFactionID,) = rec
        cfg.eveowners.Prime([charID])
        if self is None or self.destroyed:
            return 
        if self and not self.destroyed and eve.session.stationid and self.sr.state == 'lobby_guests':
            for entry in self.sr.scroll.GetNodes():
                if entry.charID == charID:
                    return 

            charinfo = cfg.eveowners.Get(charID)
            entry = listentry.Get('User', {'charID': charID,
             'info': charinfo,
             'label': charinfo.name,
             'corpID': corpID,
             'allianceID': allianceID,
             'warFactionID': warFactionID})
            self.sr.scroll.AddEntries(-1, [entry])
            self.sr.scroll.Sort('label')



    def OnCharNoLongerInStation(self, rec):
        (charID, corpID, allianceID, warFactionID,) = rec
        if self and not self.destroyed and eve.session.stationid and self.sr.state == 'lobby_guests':
            for entry in self.sr.scroll.GetNodes():
                if entry.charID == charID:
                    self.sr.scroll.RemoveEntries([entry])




    def ShowGuests(self):
        if self.sr.state != 'lobby_guests':
            return 
        guests = sm.GetService('station').GetGuests()
        owners = []
        for charID in guests.keys():
            if charID not in owners:
                owners.append(charID)

        cfg.eveowners.Prime(owners)
        if self is None or self.destroyed:
            return 
        scrolllist = []
        for charID in guests.keys():
            (corpID, allianceID, warFactionID,) = guests[charID]
            charinfo = cfg.eveowners.Get(charID)
            scrolllist.append(listentry.Get('User', {'charID': charID,
             'info': charinfo,
             'label': charinfo.name,
             'corpID': corpID,
             'allianceID': allianceID,
             'warFactionID': warFactionID}))

        self.sr.scroll.Load(contentList=scrolllist, sortby='label')



    def ShowAgents(self):
        try:
            agentsSvc = sm.StartService('agents')
            journalSvc = sm.StartService('journal')
            facWarSvc = sm.StartService('facwar')
            standingSvc = sm.StartService('standing')
            epicArcStatusSvc = sm.RemoteSvc('epicArcStatus')
            if self.sr.state != 'lobby_agents':
                return 
            agentMissions = journalSvc.GetMyAgentJournalDetails()[:1][0]
            agentsInStation = agentsSvc.GetAgentsByStationID()[eve.session.stationid]
            relevantAgents = []
            for each in agentMissions:
                (missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable,) = each
                agent = agentsSvc.GetAgentByID(agentID)
                if missionState not in (const.agentMissionStateAllocated, const.agentMissionStateOffered) or agent.agentTypeID in (const.agentTypeGenericStorylineMissionAgent,
                 const.agentTypeStorylineMissionAgent,
                 const.agentTypeEventMissionAgent,
                 const.agentTypeEpicArcAgent):
                    relevantAgents.append(agentID)

            localRelevantAgents = []
            for agent in agentsInStation:
                if agent.agentID in relevantAgents:
                    localRelevantAgents.append(agent.agentID)

            if self is None or self.destroyed:
                return 
            scrolllist = []
            sortlist = []
            for agentID in relevantAgents:
                if not eve.rookieState or agentID in const.rookieAgentList:
                    if agentID not in localRelevantAgents:
                        sortlist.append((cfg.eveowners.Get(agentID).name, listentry.Get('User', {'charID': agentID})))

            if sortlist:
                scrolllist.append(listentry.Get('Header', {'label': mls.UI_STATION_AGENTSOFINTEREST}))
                scrolllist += uiutil.SortListOfTuples(sortlist)
            unavailableAgents = []
            availableAgents = []
            for agent in agentsInStation:
                if agent.agentID in const.rookieAgentList:
                    continue
                if not eve.rookieState or agent.agentID in const.rookieAgentList:
                    isLimitedToFacWar = False
                    if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and facWarSvc.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                        isLimitedToFacWar = True
                    if agent.agentTypeID in (const.agentTypeResearchAgent,
                     const.agentTypeBasicAgent,
                     const.agentTypeEventMissionAgent,
                     const.agentTypeFactionalWarfareAgent):
                        standingIsValid = standingSvc.CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID)
                        haveMissionFromAgent = agent.agentID in relevantAgents
                        if not isLimitedToFacWar and (standingIsValid or haveMissionFromAgent):
                            availableAgents.append(agent.agentID)
                        else:
                            unavailableAgents.append(agent.agentID)
                    elif agent.agentTypeID == const.agentTypeEpicArcAgent:
                        standingIsValid = standingSvc.CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID)
                        haveMissionFromAgent = agent.agentID in relevantAgents
                        epicAgentAvailable = False
                        if haveMissionFromAgent:
                            epicAgentAvailable = True
                        elif standingIsValid:
                            if agent.agentID in relevantAgents or epicArcStatusSvc.AgentHasEpicMissionsForCharacter(agent.agentID):
                                epicAgentAvailable = True
                        if epicAgentAvailable:
                            availableAgents.append(agent.agentID)
                        else:
                            unavailableAgents.append(agent.agentID)
                    if agent.agentTypeID == const.agentTypeAura:
                        availableAgents.append(agent.agentID)
                    elif agent.agentTypeID in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
                        if agent.agentID in localRelevantAgents:
                            availableAgents.append(agent.agentID)
                        else:
                            unavailableAgents.append(agent.agentID)

            if availableAgents:
                scrolllist.append(listentry.Get('Header', {'label': mls.UI_STATION_AVAILABLETOYOU}))
                sortlist = []
                for agentID in availableAgents:
                    sortlist.append((cfg.eveowners.Get(agentID).name, listentry.Get('User', {'charID': agentID})))

                scrolllist += uiutil.SortListOfTuples(sortlist)
            if unavailableAgents:
                scrolllist.append(listentry.Get('Header', {'label': mls.UI_STATION_NOTAVAILABLETOYOU}))
                sortlist = []
                for agentID in unavailableAgents:
                    sortlist.append((cfg.eveowners.Get(agentID).name, listentry.Get('User', {'charID': agentID})))

                scrolllist += uiutil.SortListOfTuples(sortlist)
            if not self or self.destroyed:
                return 
            self.sr.scroll.Load(fixedEntryHeight=40, contentList=scrolllist)
        except:
            log.LogException()
            sys.exc_clear()



    def InteractWithAgent(self, agentID, *args):
        sm.StartService('agents').InteractWith(agentID)



    def SetHQ(self, *args):
        if sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
            raise UserError('CanNotSetHQAtPlayerOwnedStation')
        if eve.Message('MoveHQHere', {}, uiconst.YESNO) == uiconst.ID_YES:
            sm.GetService('corp').GetCorpStationManager().MoveCorpHQHere()



    def RentOffice(self, *args):
        if not self.sr.Get('isRentOfficeOpening') or not self.sr.isRentOfficeOpening:
            self.sr.isRentOfficeOpening = 1
            try:
                cost = sm.GetService('corp').GetCorpStationManager().GetQuoteForRentingAnOffice()
                if eve.Message('AskPayOfficeRentalFee', {'cost': util.FmtCurrency(cost, currency=None),
                 'days': const.rentalPeriodOffice}, uiconst.YESNO) == uiconst.ID_YES:
                    officeID = sm.GetService('corp').GetCorpStationManager().RentOffice(cost)
                    if officeID:
                        office = sm.GetService('corp').GetOffice()
                        eve.InvalidateLocationCache(officeID)
                        if office is not None:
                            folder = eve.GetInventoryFromId(office.officeFolderID)
                            folder.List()
                            sm.GetService('window').OpenCorpHangar(office.itemID)
                uthread.new(self.LoadButtons)
                if self.sr.lobbytabs.GetSelectedArgs() == 'lobby_offices':
                    self.ShowOffices()

            finally:
                self.sr.isRentOfficeOpening = 0




    def ShowShips(self):
        if self.sr.shipsContainer is None:
            return 
        self.sr.lobbytabs.ShowPanel(self.sr.shipsContainer)



    def ShowItems(self):
        if self.sr.itemsContainer is None:
            return 
        self.sr.lobbytabs.ShowPanel(self.sr.itemsContainer)



    def ShowOffices(self):
        if self.sr.Get('state', None) != 'lobby_offices':
            return 
        corpsWithOffices = sm.GetService('corp').GetCorporationsWithOfficesAtStation()
        cfg.corptickernames.Prime([ c.corporationID for c in corpsWithOffices ])
        scrolllist = []
        for corp in corpsWithOffices:
            data = util.KeyVal()
            data.corpName = corp.corporationName
            data.corpID = corp.corporationID
            data.corporation = corp
            scrolllist.append((data.corpName.lower(), listentry.Get('OfficeEntry', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        unrentedOffices = self.GetNumberOfUnrentedOffices()
        scrolllist.insert(0, listentry.Get('Header', {'label': mls.UI_GENERIC_AVAILABLEOFFICE % {'numslots': '<b>%s</b>' % unrentedOffices}}))
        if self and not self.destroyed:
            self.sr.scroll.Load(contentList=scrolllist)



    def GetLobbyScrollWidth(self):
        if not self or self.destroyed:
            return 0
        return self.sr.scroll.GetContentWidth()



    def GetNumberOfUnrentedOffices(self):
        return sm.GetService('corp').GetCorpStationManager().GetNumberOfUnrentedOffices()



    def OnCorporationMemberChanged(self, memberID, change):
        if memberID == session.charid:
            self.LoadButtons()




class OfficeEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.OfficeEntry'

    def Startup(self, *args):
        self.Flush()
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, weight=1)
        main = uicls.Container(parent=self, align=uiconst.TOTOP, height=30, state=uiconst.UI_PICKCHILDREN)
        left = uicls.Container(parent=main, align=uiconst.TOLEFT, width=50, state=uiconst.UI_PICKCHILDREN)
        uicls.Line(parent=main, align=uiconst.TOLEFT)
        icon = uicls.Container(parent=left, align=uiconst.TOPLEFT, width=32, height=32, left=3, top=3, state=uiconst.UI_PICKCHILDREN)
        par = uicls.Container(parent=main, align=uiconst.TOTOP, height=17, state=uiconst.UI_PICKCHILDREN)
        label = mls.UI_CORP_CORPNAME
        fieldName = 'corpName'
        l = uicls.Label(text=label, parent=par, left=5, top=2, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, uppercase=1)
        t = uicls.Label(text='', parent=par, left=5, state=uiconst.UI_NORMAL)
        setattr(self.sr, fieldName + '_Label', l)
        setattr(self.sr, fieldName + '_Text', t)
        setattr(self.sr, fieldName, par)
        uicls.Line(parent=self, align=uiconst.TOTOP)
        self.sr.buttonCnt = uicls.Container(parent=self, align=uiconst.TOTOP, height=25, state=uiconst.UI_HIDDEN)
        self.sr.icon = icon
        self.sr.main = main
        self.sr.infoicon = uicls.InfoIcon(size=16, left=32, top=3, parent=left, idx=0)



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.infoicon.OnClick = (uix.ShowInfo,
         const.typeCorporation,
         data.corpID,
         None)
        mainHeight = 0
        fieldName = 'corpName'
        infofield = self.sr.Get(fieldName, None)
        fieldText = self.sr.Get(fieldName + '_Text', None)
        fieldLabel = self.sr.Get(fieldName + '_Label', None)
        fieldText.text = data.Get(fieldName, '')
        fieldText.top = fieldLabel.textheight
        infofield.height = fieldText.top + fieldText.textheight + 2
        if infofield.state != uiconst.UI_HIDDEN:
            mainHeight += infofield.height
        self.sr.main.height = mainHeight + 10
        uix.Flush(self.sr.icon)

        def LogoThread():
            if self and not self.dead:
                uiutil.GetLogoIcon(itemID=data.corpID, parent=self.sr.icon, acceptNone=False, align=uiconst.TOALL)


        uthread.new(LogoThread)
        uix.Flush(self.sr.buttonCnt)
        if not util.IsNPC(node.corpID):
            buttonEntries = []
            if eve.session.corpid != node.corpID:
                buttonEntries.append((mls.UI_CMD_APPLYTOJOIN,
                 sm.GetService('corp').ApplyForMembership,
                 (node.corpID,),
                 80))
            if len(buttonEntries) > 0:
                uicls.Line(parent=self.sr.buttonCnt, align=uiconst.TOBOTTOM)
                self.sr.buttonCnt.state = uiconst.UI_PICKCHILDREN
                self.sr.buttons = uicls.ButtonGroup(btns=buttonEntries, parent=self.sr.buttonCnt, unisize=0, line=0)
                self.sr.buttons.top -= 1
            else:
                self.sr.buttonCnt.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.buttonCnt.state = uiconst.UI_HIDDEN



    def GetHeight(self, *args):
        (node, width,) = args
        height = 2
        lh = uix.GetTextHeight(mls.UI_CORP_CORPNAME, autoWidth=1, fontsize=9, uppercase=1)
        th = uix.GetTextHeight(node.corpName, autoWidth=1)
        multiplier = 1
        height += (lh + th + 15) * multiplier
        height += 5
        if not util.IsNPC(node.corpID) and eve.session.corpid != node.corpID:
            height += 30
        node.height = height
        return node.height




class DropDude(uicls.SE_BaseClassCore):
    __guid__ = 'xtriui.DropDude'
    default_align = uiconst.TOALL

    def OnDropData(self, dragObj, nodes):
        if not len(self.children):
            return 
        if hasattr(self.children[0], 'OnDropData'):
            self.children[0].OnDropData(dragObj, nodes)




