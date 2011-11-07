import uix
import uthread
import blue
import util
import triui
import form
import copy
import moniker
import weakref
import service
import uicls
from service import ROLE_SERVICE, ROLE_IGB
import uiconst
globals().update(service.consts)

class Agents(service.Service):
    __exportedcalls__ = {'InteractWith': [],
     'NamePopup': [ROLE_SERVICE],
     'GetQuantity': [ROLE_SERVICE],
     'PopupSelect': [ROLE_SERVICE],
     'YesNo': [ROLE_SERVICE],
     'MessageBox': [ROLE_SERVICE],
     'SingleChoiceBox': [ROLE_SERVICE],
     'CheckCargoCapacity': [ROLE_SERVICE],
     'GetAgentByID': [],
     'GetAgentsByID': [],
     'GetAgentsByStationID': [],
     'GetAgentsByCorpID': [],
     'IsAgent': [],
     'GetDivisions': [],
     'GetTutorialAgentIDs': [],
     'DoAction': [ROLE_IGB],
     'PopupMissionJournal': [ROLE_IGB | ROLE_SERVICE],
     'RemoveOfferFromJournal': [],
     'ShowMissionObjectives': [ROLE_IGB | ROLE_SERVICE],
     'PopupDungeonShipRestrictionList': [ROLE_IGB | ROLE_SERVICE]}
    __configvalues__ = {'printHTML': 0}
    __guid__ = 'svc.agents'
    __servicename__ = 'agents'
    __displayname__ = 'Agent Service'
    __dependencies__ = []
    __notifyevents__ = ['OnAgentMissionChange', 'OnSessionChanged', 'OnInteractWith']

    def __GetAllAgents(self):
        if self.allAgents is None:
            t = sm.RemoteSvc('agentMgr').GetAgents()
            newRowSet = util.Rowset(t.columns)
            for r in t:
                newRowSet.lines.append(list(r))

            newRowSet.AddField('factionID', None)
            newRowSet.AddField('solarsystemID', None)
            for each in newRowSet:
                if not util.IsStation(each.stationID):
                    continue
                if each.stationID:
                    station = sm.GetService('ui').GetStation(each.stationID)
                    each.corporationID = each.corporationID or station.ownerID
                    each.solarsystemID = station.solarSystemID
                each.factionID = sm.GetService('faction').GetFaction(each.corporationID)

            self.allAgentsByID = newRowSet.Index('agentID')
            self.allAgentsByStationID = newRowSet.Filter('stationID')
            self.allAgentsByCorpID = newRowSet.Filter('corporationID')
            self.allAgents = newRowSet



    def GetAgentByID(self, agentID):
        self._Agents__GetAllAgents()
        if agentID in self.allAgentsByID:
            return self.allAgentsByID[agentID]



    def GetAgentsByID(self):
        self._Agents__GetAllAgents()
        return self.allAgentsByID



    def GetAgentsByStationID(self):
        self._Agents__GetAllAgents()
        return self.allAgentsByStationID



    def GetAgentsByCorpID(self, corpID):
        self._Agents__GetAllAgents()
        return self.allAgentsByCorpID[corpID]



    def IsAgent(self, agentID):
        self._Agents__GetAllAgents()
        return agentID in self.allAgentsByID



    def GetAgentDisplayName(self, agentID):
        agentInfo = self.GetAgentByID(agentID)
        if agentInfo is not None and agentInfo.agentTypeID == const.agentTypeAura:
            return 'Aura'
        else:
            return cfg.eveowners.Get(agentID).name



    def GetDivisions(self):
        if self.divisions is None:
            self.divisions = sm.RemoteSvc('corporationSvc').GetNPCDivisions().Index('divisionID')
            if prefs.languageID != 'EN':
                for row in self.divisions.values():
                    row.divisionName = Tr(row.divisionName, 'dbo.crpNPCDivisions.divisionName', row.divisionID)
                    row.leaderType = Tr(row.leaderType, 'dbo.crpNPCDivisions.leaderType', row.divisionID)

        return self.divisions



    def __init__(self):
        service.Service.__init__(self)
        self.windows = {}
        self.allAgents = None
        self.divisions = None
        self.agentMonikers = {}
        self.lastMonikerAccess = blue.os.GetTime()
        uthread.worker('agents::ClearMonikers', self._Agents__ClearAgentMonikers)



    def GetAgentMoniker(self, agentID):
        if agentID not in self.agentMonikers:
            if getattr(self, 'allAgentsByID', False) and agentID in self.allAgentsByID and agentID in self.allAgentsByID and self.allAgentsByID[agentID].stationID:
                self.agentMonikers[agentID] = moniker.GetAgent(agentID, self.allAgentsByID[agentID].stationID)
            else:
                self.agentMonikers[agentID] = moniker.GetAgent(agentID)
        self.lastMonikerAccess = blue.os.GetTime()
        return self.agentMonikers[agentID]



    def __ClearAgentMonikers(self):
        while self.state == service.SERVICE_RUNNING:
            blue.pyos.synchro.Sleep(300000)
            if blue.os.GetTime() + 30 * MIN < self.lastMonikerAccess:
                self.agentMonikers.clear()




    def Run(self, memStream = None):
        self.LogInfo('Agent Service')
        self.processing = 0
        self.reentrancyGuard1 = 0
        self.reentrancyGuard2 = 0
        self.journalwindows = weakref.WeakValueDictionary()
        self.agentSolarSystems = {}



    def CheckCargoCapacity(self, cargoUnits, mandatoryCargoUnits):
        activeShipID = util.GetActiveShip()
        if activeShipID is None:
            (capacity, used,) = (0, 0)
        else:
            (capacity, used,) = sm.GetService('invCache').GetInventoryFromId(activeShipID).GetCapacity(const.flagCargo)
        if session.stationid2 is None and capacity - (used + mandatoryCargoUnits) < 0:
            rejectMessage = mls.AGT_STANDARDMISSION_ACCEPT_CARGOCAPWARNING_DIALOGUE % {'external.mandatorycargounits': '%-2.2f' % mandatoryCargoUnits}
            self.MessageBox(mls.AGT_STANDARDMISSION_ACCEPT_FAILURE_TITLE, rejectMessage)
            return ('mission.offeredinsufficientcargospace', rejectMessage)
        if capacity - (used + cargoUnits) < 0:
            if capacity - (used + cargoUnits) < 1:
                c1 = '%-2.2f' % cargoUnits
                c2 = '%-2.2f' % (capacity - used)
            else:
                c1 = cargoUnits
                c2 = capacity - used
            if not self.YesNo(mls.AGT_STANDARDMISSION_ACCEPT_CARGOCAPWARNING_TITLE, mls.AGT_STANDARDMISSION_ACCEPT_CARGOCAPWARNING_MESSAGE % {'external.required': c1,
             'external.available': c2}, 'AgtMissionAcceptBigCargo'):
                return 'mission.offered'



    def YesNo(self, title, body, suppressID = None):
        options = {'text': body,
         'title': title,
         'buttons': uiconst.YESNO,
         'icon': uiconst.QUESTION}
        ret = self.ShowMessageWindow(options, suppressID)
        return ret == uiconst.ID_YES



    def MessageBox(self, title, body, suppressID = None):
        options = {'text': body,
         'title': title,
         'buttons': triui.OK,
         'icon': triui.INFO}
        self.ShowMessageWindow(options, suppressID)



    def ShowMessageWindow(self, options, suppressID = None):
        if suppressID:
            supp = settings.user.suppress.Get('suppress.' + suppressID, None)
            if supp is not None:
                return supp
            options['suppText'] = mls.UI_SHARED_SUPPRESS2
        (ret, block,) = sm.StartService('gameui').MessageBox(**options)
        if suppressID and block and ret not in [uiconst.ID_NO]:
            settings.user.suppress.Set('suppress.' + suppressID, ret)
        return ret



    def SingleChoiceBox(self, title, body, choices, suppressID = None):
        options = {'text': body,
         'title': title,
         'icon': triui.QUESTION,
         'buttons': uiconst.OKCANCEL,
         'radioOptions': choices}
        if suppressID:
            supp = settings.user.suppress.Get('suppress.' + suppressID, None)
            if supp is not None:
                return supp
            options['suppText'] = mls.UI_SHARED_SUPPRESS4
        (ret, block,) = sm.StartService('gameui').RadioButtonMessageBox(**options)
        if suppressID and block:
            settings.user.suppress.Set('suppress.' + suppressID, ret)
        return (ret[0] == uiconst.ID_OK, ret[1])



    def GetQuantity(self, **keywords):
        ret = uix.QtyPopup(**keywords)
        if not ret:
            return None
        return ret.get('qty', None)



    def NamePopup(self, *args, **keywords):
        ret = uix.NamePopup(*args, **keywords)
        if ret is not None:
            return ret['name']
        else:
            return 



    def PopupSelect(self, title, explanation, **keywords):
        if 'typeIDs' in keywords:
            displayList = []
            for typeID in keywords['typeIDs']:
                displayList.append([cfg.invtypes.Get(typeID).name, typeID, typeID])

            ret = uix.ListWnd(displayList, 'type', title, explanation, 0, 300)
        else:
            return None
        if ret:
            return ret[2]
        else:
            return None



    def Stop(self, memStream = None):
        self.LogInfo('Stopping Agent Services')
        service.Service.Stop(self)


    rookieAgentDict = {}

    def GetTutorialAgentIDs(self):
        if self.rookieAgentDict == {}:
            for agentID in const.rookieAgentList:
                self.rookieAgentDict[agentID] = True

        return copy.copy(self.rookieAgentDict)



    def GetAuraAgentID(self):
        charinfo = sm.RemoteSvc('charMgr').GetPublicInfo(eve.session.charid)
        schoolinfo = sm.GetService('cc').GetData('schools', ['schoolID', charinfo.schoolID])
        corpinfo = sm.GetService('corp').GetCorporation(schoolinfo.corporationID)
        agents = self.allAgentsByStationID[corpinfo.stationID]
        for agent in agents:
            if agent.agentTypeID == const.agentTypeAura:
                return agent.agentID




    def OnInteractWith(self, agentID):
        self.InteractWith(agentID)



    def InteractWith(self, agentID, maximize = True):
        agentDialogueWindow = None
        if agentID in self.windows:
            agentDialogueWindow = self.windows[agentID]
            if agentDialogueWindow.destroyed:
                agentDialogueWindow = None
            if agentDialogueWindow is not None and not agentDialogueWindow.destroyed:
                if maximize:
                    agentDialogueWindow.Maximize()
        if agentDialogueWindow is None:
            agentDialogueWindow = self.OpenAgentDialogueWindow(windowName='agentinteraction_%s' % agentID, agentID=agentID)
            self.windows[agentID] = agentDialogueWindow
            agentDialogueWindow.sr.main.opacity = 0.0
            if agentID not in self.GetTutorialAgentIDs() and sm.GetService('agents').GetAgentByID(agentID).agentTypeID != const.agentTypeAura:
                uthread.pool('agents::confirm', eve.Message, 'AgtMissionOfferWarning')
        self._Agents__Interact(agentDialogueWindow)
        if not agentDialogueWindow.destroyed:
            agentDialogueWindow.sr.main.opacity = 1.0
        if not agentDialogueWindow.destroyed and hasattr(agentDialogueWindow.sr, 'stack') and agentDialogueWindow.sr.stack:
            agentDialogueWindow.RefreshBrowsers()



    def __GetConversation(self, wnd, actionID):
        if wnd is None or wnd.destroyed or wnd.sr is None:
            return (None, None, None)
        tmp = wnd.sr.agentMoniker.DoAction(actionID)
        if wnd is None or wnd.destroyed or wnd.sr is None:
            return (None, None, None)
        (ret, wnd.sr.oob,) = tmp
        (wnd.sr.agentSays, wnd.sr.dialogue,) = ret
        if actionID is None and len(wnd.sr.dialogue):
            self.LogInfo('Agent Service: Started a new conversation with an agent and successfully retrieved dialogue options.')
            firstActionID = wnd.sr.dialogue[0][0]
            firstActionDialogue = wnd.sr.dialogue[0][1]
            agentHasLocatorService = False
            for (id, dlg,) in wnd.sr.dialogue:
                if mls.AGT_LOCATECHARACTER in dlg:
                    agentHasLocatorService = True

            isResearchAgent = False
            if self.GetAgentByID(wnd.sr.agentID).agentTypeID == const.agentTypeResearchAgent:
                isResearchAgent = True
            if mls.AGT_STANDARDMISSION_ASK in firstActionDialogue and not agentHasLocatorService and not isResearchAgent:
                self.LogInfo("Agent Service: Automatically executing the 'Ask' dialogue action for the player.")
                tmp = wnd.sr.agentMoniker.DoAction(firstActionID)
                if wnd is None or wnd.destroyed or wnd.sr is None:
                    return (None, None, None)
                (ret, wnd.sr.oob,) = tmp
                (wnd.sr.agentSays, wnd.sr.dialogue,) = ret
        return (wnd.sr.agentSays, wnd.sr.dialogue, wnd.sr.oob)



    def DoAction(self, agentID, actionID = None, closeWindowOnClick = False):
        if self.reentrancyGuard1:
            return 
        self.reentrancyGuard1 = 1
        try:
            if agentID in self.windows:
                self._Agents__Interact(self.windows[agentID], actionID, closeWindowAfterInteraction=closeWindowOnClick)

        finally:
            self.reentrancyGuard1 = 0




    def OnAgentMissionChange(self, what, agentID, tutorialID = None):
        if tutorialID:
            sm.GetService('tutorial').OpenTutorialSequence_Check(tutorialID, force=1)
        if (agentID, 'offer') in self.journalwindows:
            window = self.journalwindows[(agentID, 'offer')]
            if window is not None and not window.destroyed:
                if what in (const.agentMissionReset,
                 const.agentMissionOfferRemoved,
                 const.agentMissionOfferExpired,
                 const.agentMissionOfferDeclined,
                 const.agentMissionOfferAccepted):
                    window.SelfDestruct()
                else:
                    self.PopupOfferJournal(agentID)
        elif (agentID, 'mission') in self.journalwindows:
            window = self.journalwindows[(agentID, 'mission')]
            if window is not None and not window.destroyed:
                if what in (const.agentMissionReset,
                 const.agentMissionDeclined,
                 const.agentMissionCompleted,
                 const.agentMissionQuit,
                 const.agentMissionFailed,
                 const.agentMissionOffered,
                 const.agentMissionOfferRemoved):
                    window.SelfDestruct()
                else:
                    self.PopupMissionJournal(agentID)
        if agentID in self.windows:
            agentDialogueWindow = self.windows[agentID]
            if what in (const.agentMissionDeclined, const.agentMissionQuit) and 'objectiveBrowser' in agentDialogueWindow.htmlCache:
                del agentDialogueWindow.htmlCache['objectiveBrowser']
            if what in (const.agentMissionOfferRemoved, const.agentMissionReset, const.agentTalkToMissionCompleted):
                if not agentDialogueWindow.destroyed:
                    agentDialogueWindow.CloseX()
                del self.windows[agentID]



    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change:
            for (key, window,) in self.journalwindows.iteritems():
                (agentID, missionState,) = key
                if window is not None and not window.destroyed:
                    self.UpdateMissionJournal(agentID, popup=False)




    def PopupMissionJournal(self, agentID, charID = None, contentID = None):
        self.UpdateMissionJournal(agentID, charID, contentID)



    def UpdateMissionJournal(self, agentID, charID = None, contentID = None, popup = True):
        if self.reentrancyGuard2:
            return 
        self.reentrancyGuard2 = 1
        try:
            ret = self.GetAgentMoniker(agentID).GetMissionJournalInfo(charID, contentID)
            if ret:
                ret = self.InsertSecurityWarning(ret)
                html = ret.html
                if (agentID, 'mission') not in self.journalwindows or self.journalwindows[(agentID, 'mission')].destroyed:
                    browser = sm.GetService('window').GetWindow('%s - %s' % (mls.AGT_MISSIONJOURNAL_CAPTION_PREFIX, self.GetAgentDisplayName(agentID)), decoClass=form.AgentBrowser, create=1, maximize=1)
                    self.journalwindows[(agentID, 'mission')] = browser
                else:
                    browser = self.journalwindows[(agentID, 'mission')]
                browser.SetMinSize([420, 400])
                uthread.new(self.LoadPage, browser, html, popup)

        finally:
            self.reentrancyGuard2 = 0




    def PopupDungeonShipRestrictionList(self, agentID, charID = None, dungeonID = None):
        restrictions = self.GetAgentMoniker(agentID).GetDungeonShipRestrictions(dungeonID)
        title = mls.AGT_STANDARDMISSION_GETJOURNALINFO_DUNGEONOBJECTIVE_PERMITTEDSHIPS_HEADER
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        ship = None
        shipID = util.GetActiveShip()
        if shipID is not None:
            ship = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItem(shipID)
        if ship:
            shipGroupID = getattr(ship, 'groupID', None)
            if shipGroupID:
                if shipGroupID in restrictions.restrictedShipTypes:
                    fontTagOpen = '<font color=#E3170D>'
                    fontTagClose = '</font>'
                    body = mls.AGT_STANDARDMISSION_GETJOURNALINFO_DUNGEONOBJECTIVE_PERMITTEDSHIPLIST_PLAYERSHIPISRESTRICTED % {'external.fontTagOpen': fontTagOpen,
                     'external.fontTagClose': fontTagClose,
                     'external.shipType': cfg.invtypes.Get(ship.typeID).name}
                elif shipGroupID in restrictions.allowedShipTypes:
                    if len(restrictions.allowedShipTypes) > 1:
                        body = mls.AGT_STANDARDMISSION_GETJOURNALINFO_DUNGEONOBJECTIVE_PERMITTEDSHIPLIST_PLAYERSHIPISNOTRESTRICTED % {'external.shipType': cfg.invtypes.Get(ship.typeID).name}
                    else:
                        restrictions.allowedShipTypes.remove(shipGroupID)
                        body = mls.AGT_STANDARDMISSION_GETJOURNALINFO_DUNGEONOBJECTIVE_PERMITTEDSHIP_PLAYERSHIPISNOTRESTRICTED % {'external.shipGroup': cfg.invgroups.Get(shipGroupID).groupName,
                         'external.shipType': cfg.invtypes.Get(ship.typeID).name}
        else:
            body = mls.AGT_STANDARDMISSION_GETJOURNALINFO_DUNGEONOBJECTIVE_PERMITTEDSHIPLIST
        body += '<br><br>'
        permittedShipTypeList = []
        for shipGroupID in restrictions.allowedShipTypes:
            permittedShipTypeList.append(cfg.invgroups.Get(shipGroupID).groupName)

        permittedShipTypeList.sort()
        body += '<ul>'
        for each in permittedShipTypeList:
            body += '<li>' + each + '</li>'

        body += '</ul>'
        self.MessageBox(title, body)



    def RemoveOfferFromJournal(self, agentID):
        self.GetAgentMoniker(agentID).RemoveOfferFromJournal()



    def OpenAgentDialogueWindow(self, windowName = 'agentDialogueWindow', agentID = None):
        window = sm.StartService('window').GetWindow(windowName, decoClass=form.AgentDialogueWindow, maximize=1, create=1)
        window.SetAgentID(agentID)
        return window



    def LoadPage(self, browser, html, popup):
        if browser.state != uiconst.UI_NORMAL and popup:
            browser.Maximize()
        if browser.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            blue.pyos.synchro.Yield()
            browser.sr.browser.LoadHTML(html)



    def PopupOfferJournal(self, agentID):
        if self.reentrancyGuard2:
            return 
        self.reentrancyGuard2 = 1
        try:
            html = self.GetAgentMoniker(agentID).GetOfferJournalInfo()
            if html:
                if self.printHTML:
                    print '-----------------------------------------------------------------------------------'
                    print html
                    print '-----------------------------------------------------------------------------------'
                if (agentID, 'offer') not in self.journalwindows or self.journalwindows[(agentID, 'offer')].destroyed:
                    browser = sm.GetService('window').GetWindow('%s - %s' % (mls.AGT_OFFERJOURNAL_CAPTION_PREFIX, self.GetAgentDisplayName(agentID)), decoClass=form.AgentBrowser, create=1, maximize=1)
                    self.journalwindows[(agentID, 'offer')] = browser
                else:
                    browser = self.journalwindows[(agentID, 'offer')]
                browser.SetMinSize([420, 400])
                browser.sr.browser.LoadHTML(html)

        finally:
            self.reentrancyGuard2 = 0




    def ShowMissionObjectives(self, agentID, charID = None, contentID = None):
        if agentID not in self.windows:
            self.InteractWith(agentID)
            return 
        if self.reentrancyGuard2:
            return 
        self.reentrancyGuard2 = 1
        try:
            agentDialogueWindow = self.windows[agentID]
            ret = self.GetAgentMoniker(agentID).GetMissionObjectiveInfo(charID, contentID)
            if not agentDialogueWindow.destroyed:
                if ret:
                    ret = self.InsertSecurityWarning(ret)
                    html = ret.html
                    agentDialogueWindow.SetDoublePaneView()
                    agentDialogueWindow.LoadHTML(html, where='objectiveBrowser')
                else:
                    agentDialogueWindow.SetSinglePaneView()

        finally:
            self.reentrancyGuard2 = 0




    def InsertSecurityWarning(self, ret):
        locations = ret.locations
        routeStart = eve.session.solarsystemid2
        charSecStatus = sm.GetService('standing').GetMySecurityRating()
        secWarning = ''
        for each in locations:
            if len(secWarning) > 0:
                break
            route = []
            if routeStart == eve.session.solarsystemid2 and each != eve.session.solarsystemid2:
                route = sm.GetService('pathfinder').GetPathBetween(eve.session.solarsystemid2, each)
            elif routeStart == eve.session.solarsystemid2 and each == eve.session.solarsystemid2:
                pass
            else:
                route = sm.GetService('pathfinder').GetPathBetween(routeStart, each)
            if route is None:
                secWarning += ' <font color=#E3170D>(%s)</font>' % mls.AGT_UTILS_NOROUTEWARNING
            elif len(route) > 0:
                routeStart = route[(len(route) - 1)]
                for solarsystem in route:
                    s = sm.GetService('map').GetItem(solarsystem)
                    if len(secWarning) > 0:
                        break
                    if charSecStatus > -5.0 and sm.StartService('map').GetSecurityClass(solarsystem) <= const.securityClassLowSec:
                        secWarning += ' <font color=#E3170D>(%s)</font>' % mls.AGT_UTILS_ROUTELOWSECWARNING
                    elif charSecStatus < -5.0 and sm.StartService('map').GetSecurityClass(solarsystem) == const.securityClassHighSec:
                        secWarning += ' <font color=#E3170D>(%s)</font>' % mls.AGT_UTILS_ROUTEHIGHSECWARNING


        if ret.html:
            ret.html = ret.html.replace('LOWSECREPLACE', secWarning)
            if self.printHTML:
                print '-----------------------------------------------------------------------------------'
                print ret.html
                print '-----------------------------------------------------------------------------------'
        return ret



    def GetMissionBriefingInformation(self, wnd):
        if wnd is None or wnd.destroyed or wnd.sr is None:
            return (None, None)
        return wnd.sr.agentMoniker.GetMissionBriefingInfo()



    def __Interact(self, agentDialogueWindow, actionID = None, closeWindowAfterInteraction = False):
        if actionID:
            agentDialogueWindow.DisableButtons()
        (agentSays, dialogue, extraInfo,) = self._Agents__GetConversation(agentDialogueWindow, actionID)
        briefingInformation = self.GetMissionBriefingInformation(agentDialogueWindow)
        initialContentID = None
        if agentSays is None:
            return 
        if closeWindowAfterInteraction:
            agentDialogueWindow.CloseX()
            return 
        if extraInfo.get('missionQuit', None):
            agentDialogueWindow.CloseX()
            return 
        customAgentButtons = {'okLabel': [],
         'okFunc': [],
         'args': []}
        disabledButtons = []
        charSays = ''
        extraMissionInfo = ''
        numDialogChoices = 0
        isAgentInteractionMission = False
        if dialogue:
            charSays = '<OL>'
            for each in dialogue:
                if not agentDialogueWindow or agentDialogueWindow.destroyed:
                    return 
                if type(each[1]) == dict:
                    if not isAgentInteractionMission:
                        initialContentID = each[1]['ContentID']
                        extraMissionInfo += '<BR>'
                    isAgentInteractionMission = True
                    extraMissionInfo += '<span id=subheader><a href="localsvc:service=agents&method=DoAction&agentID=%d&actionID=%d">%s</a> &gt;&gt;</span><br>' % (agentDialogueWindow.sr.agentID, each[0], each[1]['Mission Title'])
                    extraMissionInfo += each[1]['Mission Briefing']
                    numDialogChoices += 1
                elif '[Button]' in each[1]:
                    label = each[1].replace('[Button]', '')
                    closeWindowOnClick = False
                    if '[CloseOnClick]' in label:
                        label = label.replace('[CloseOnClick]', '')
                        closeWindowOnClick = True
                    if '[Disabled]' in label:
                        label = label.replace('[Disabled]', '')
                        disabledButtons.append(label)
                    customAgentButtons['okLabel'].append(label)
                    customAgentButtons['okFunc'].append(self.DoAction)
                    customAgentButtons['args'].append((agentDialogueWindow.sr.agentID, each[0], closeWindowOnClick))
                else:
                    charSays += '<li><a href="localsvc:service=agents&method=DoAction&agentID=%d&actionID=%d">%s</a></li><br>' % (agentDialogueWindow.sr.agentID, each[0], each[1])
                    numDialogChoices += 1

            charSays += '</OL>'
        if numDialogChoices < 2:
            charSays = charSays.replace('<li>', '')
            charSays = charSays.replace('</li>', '')
            alignCharSays = 'align=center'
        else:
            alignCharSays = ''
        a = self.GetAgentByID(agentDialogueWindow.sr.agentID)
        agentCorpID = a.corporationID
        agentDivision = self.GetDivisions()[a.divisionID].divisionName.replace('&', '&amp;')
        s = [sm.GetService('standing').GetEffectiveStanding(a.factionID, eve.session.charid)[0], sm.GetService('standing').GetEffectiveStanding(a.corporationID, eve.session.charid)[0], sm.GetService('standing').GetEffectiveStanding(a.agentID, eve.session.charid)[0]]
        if min(*s) <= -2.0:
            effectiveStanding = '<b>%-2.1f</b>' % min(*s)
        else:
            effectiveStanding = '%-2.1f' % max(sm.GetService('standing').GetEffectiveStanding(a.factionID, eve.session.charid)[0], sm.GetService('standing').GetEffectiveStanding(a.corporationID, eve.session.charid)[0], sm.GetService('standing').GetEffectiveStanding(a.agentID, eve.session.charid)[0]) or 0.0
        if getattr(agentDialogueWindow.sr, 'oob', {}).get('loyaltyPoints', 0):
            loyaltyPoints = '<TR><TD>%s</TD><TD>%s</TD></TR>' % (mls.AGT_DIALOGUE_LOYALTYPOINTS, getattr(agentDialogueWindow.sr, 'oob', {}).get('loyaltyPoints', 0))
        else:
            loyaltyPoints = ''
        agentBloodline = sm.GetService('cc').GetData('bloodlines', ['bloodlineID', a.bloodlineID])
        agentRace = sm.GetService('cc').GetData('races', ['raceID', agentBloodline.raceID])
        raceName = Tr(agentRace.raceName, 'character.races.raceName', agentRace.dataID)
        bloodlineName = Tr(agentBloodline.bloodlineName, 'character.bloodlines.bloodlineName', agentBloodline.dataID)
        if isAgentInteractionMission:
            extraMissionInfo += '<BR>'
            if briefingInformation['Decline Warning']:
                extraMissionInfo += briefingInformation['Decline Warning']
            else:
                extraMissionInfo += briefingInformation['Expiration Message']
        elif briefingInformation:
            extraMissionInfo += '<BR>'
            if briefingInformation['Decline Warning']:
                extraMissionInfo += briefingInformation['Decline Warning']
            else:
                extraMissionInfo += briefingInformation['Expiration Message']
            extraMissionInfo += '<br><center>%(external.missionImage)s</center>' % {'external.missionImage': briefingInformation['Mission Image']}
        if not len(customAgentButtons['okLabel']) and not isAgentInteractionMission:
            extraMissionInfo = ''
        missionTitle = ''
        if briefingInformation:
            missionTitle = '<BR><span id=subheader>' + briefingInformation['Mission Title'] + '</span><BR>'
        if self.GetAgentByID(agentDialogueWindow.sr.agentID).agentTypeID == const.agentTypeAura:
            agentInfoIcon = ''
            conversationTitle = '%s - %s' % (mls.AGT_DIALOGUE_BLURBCONVERSATION, 'Aura')
            blurbEffectiveStanding = ''
            blurbDivision = ''
        else:
            agentInfoIcon = '<a href=showinfo:%d//%d><img src=icon:38_208 size=16 alt="%s"></a>' % (self.GetAgentInventoryTypeByBloodline(a.bloodlineID), a.agentID, mls.UI_CMD_SHOWINFO)
            conversationTitle = '%s - %s' % (mls.AGT_DIALOGUE_BLURBCONVERSATION, cfg.eveowners.Get(agentDialogueWindow.sr.agentID).name)
            blurbEffectiveStanding = mls.AGT_DIALOGUE_EFFECTIVESTANDING % {'external.effectiveStanding': effectiveStanding}
            blurbDivision = mls.AGT_DIALOGUE_AGENTDIVISION % {'external.agentDivision': agentDivision}
        agentLocationWrap = self.GetAgentMoniker(agentDialogueWindow.sr.agentID).GetAgentLocationWrap()
        props = {'agentCorpName': cfg.eveowners.Get(agentCorpID).name,
         'agentName': sm.GetService('agents').GetAgentDisplayName(agentDialogueWindow.sr.agentID),
         'agentLevel': a.level,
         'agentRace': raceName,
         'agentBloodline': bloodlineName,
         'agentInfoIcon': agentInfoIcon,
         'agentLocation': agentLocationWrap,
         'charName': cfg.eveowners.Get(eve.session.charid).name,
         'corpName': cfg.eveowners.Get(eve.session.corpid).name,
         'agentSays': agentSays,
         'charSays': charSays,
         'alignCharSays': alignCharSays,
         'agentID': agentDialogueWindow.sr.agentID,
         'agentCorpID': agentCorpID,
         'loyaltyPoints': loyaltyPoints,
         'extraMissionInfo': extraMissionInfo,
         'conversationTitle': conversationTitle,
         'blurbName': mls.AGT_DIALOGUE_BLURBNAME,
         'blurbCorporation': mls.AGT_DIALOGUE_BLURBCORPORATION,
         'blurbDivision': blurbDivision,
         'blurbRace': mls.AGT_DIALOGUE_BLURBRACE,
         'blurbBloodline': mls.AGT_DIALOGUE_BLURBBLOODLINE,
         'blurbEffectiveStanding': blurbEffectiveStanding,
         'missionTitle': missionTitle}
        head = '\n<HTML>\n<HEAD>\n<LINK REL="stylesheet" TYPE="text/css" HREF="res:/ui/css/agentconvo.css">\n<TITLE>%(conversationTitle)s</TITLE>\n</HEAD>\n<BODY background-color=#00000000 link=#FFA800>\n' % props
        body = '\n    <TABLE border=0 cellpadding=1 cellspacing=1>\n        <TR>\n            <TD valign=top >\n                <TABLE border=0 cellpadding=1 cellspacing=1>\n                    <TR>\n                    </TR>\n                    <TR>\n                    </TR>\n                    <TR>\n                    </TR>\n                    <TR>\n                        <TD valign=top><img src="portrait:%(agentID)d" width=120 height=120 size=256 align=left style=margin-right:10></TD>\n                    </TR>\n                </TABLE>\n            </TD>\n            <TD valign=top>\n                    <TABLE border=0 width=290 cellpadding=1 cellspacing=1>\n                    <TR>\n                        <TD width=120 valign=top colspan=2><font size=24>%(agentName)s</font> %(agentInfoIcon)s</TD>\n                    </TR>\n                    <TR>\n                        <TD>%(blurbDivision)s</TD>\n                    </TR>\n                    <TR>\n                        <TD height=12> </TD>\n                    </TR>\n                    <TR>\n                        <TD>%(agentLocation)s</TD>\n                    </TR>\n                    <TR>\n                        <TD height=12> </TD>\n                    </TR>\n                    <TR>\n                        <TD>%(blurbEffectiveStanding)s</TD>\n                    </TR>\n                    %(loyaltyPoints)s\n                </TABLE>\n            </TD>\n        </TR>\n    </TABLE>\n\n    <table width=380 cellpadding=2>\n    <tr>\n        <td>\n            %(missionTitle)s\n            <div id=basetext><font size=12>%(agentSays)s</font></div>\n        </td>\n    </tr>\n    </table>\n    <TABLE width="380">\n        <TR>\n            <TD>\n                %(extraMissionInfo)s\n            </TD>\n        </TR>\n        <TR>\n            <TD %(alignCharSays)s>\n                <BR>\n                %(charSays)s\n            </TD>\n        </TR>\n    </TABLE>\n        ' % props
        foot = '\n</BODY>\n</HTML>\n        ' % props
        html = head + body + foot
        if self.printHTML:
            print '-----------------------------------------------------------------------------------'
            print html
            print '-----------------------------------------------------------------------------------'
        numButtons = len(customAgentButtons['okLabel'])
        if numButtons < 3:
            for each in (mls.AGT_STANDARDMISSION_ASK, mls.AGT_STANDARDMISSION_QUIT, mls.AGT_STANDARDMISSION_CONTINUE):
                if each in customAgentButtons['okLabel']:
                    customAgentButtons['okLabel'].append(mls.UI_CMD_CLOSE)
                    customAgentButtons['okFunc'].append(agentDialogueWindow.CloseX)
                    customAgentButtons['args'].append('self')
                    break

        if numButtons:
            agentDialogueWindow.DefineButtons('Agent Interaction Buttons', **customAgentButtons)
            for each in disabledButtons:
                agentDialogueWindow.DisableButton(each)

        else:
            agentDialogueWindow.DefineButtons(uiconst.CLOSE)
        ret = self.GetAgentMoniker(agentDialogueWindow.sr.agentID).GetMissionObjectiveInfo()
        if agentDialogueWindow and not agentDialogueWindow.destroyed:
            agentDialogueWindow.SetHTML(html, where='briefingBrowser')
            objectiveHtml = None
            if ret and not (extraInfo['missionCompleted'] or extraInfo['missionDeclined'] or extraInfo['missionQuit']):
                objectiveHtml = self.InsertSecurityWarning(ret).html
                agentDialogueWindow.SetHTML(objectiveHtml, where='objectiveBrowser')
            if objectiveHtml or extraInfo.get('missionCompleted'):
                agentDialogueWindow.SetDoublePaneView(briefingHtml=html, objectiveHtml=objectiveHtml)
            else:
                agentDialogueWindow.SetSinglePaneView(briefingHtml=html)



    def GetAgentInventoryTypeByBloodline(self, bloodlineID):
        return {const.bloodlineAmarr: const.typeCharacterAmarr,
         const.bloodlineNiKunni: const.typeCharacterNiKunni,
         const.bloodlineCivire: const.typeCharacterCivire,
         const.bloodlineDeteis: const.typeCharacterDeteis,
         const.bloodlineGallente: const.typeCharacterGallente,
         const.bloodlineIntaki: const.typeCharacterIntaki,
         const.bloodlineSebiestor: const.typeCharacterSebiestor,
         const.bloodlineBrutor: const.typeCharacterBrutor,
         const.bloodlineStatic: const.typeCharacterStatic,
         const.bloodlineModifier: const.typeCharacterModifier,
         const.bloodlineAchura: const.typeCharacterAchura,
         const.bloodlineJinMei: const.typeCharacterJinMei,
         const.bloodlineKhanid: const.typeCharacterKhanid,
         const.bloodlineVherokior: const.typeCharacterVherokior}[bloodlineID]



    def GetSolarSystemOfAgent(self, agentID):
        if agentID not in self.agentSolarSystems:
            self.agentSolarSystems[agentID] = sm.RemoteSvc('agentMgr').GetSolarSystemOfAgent(agentID)
        return self.agentSolarSystems[agentID]




class AgentBrowser(uicls.Window):
    __guid__ = 'form.AgentBrowser'
    __notifyevents__ = []

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'all'
        self.loadupdates = 0
        self.statustext = ''
        self.views = []
        self.activeView = 0
        self.SetCaption('')
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        self.sr.browser = uicls.Edit(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), readonly=1)
        self.sr.browser.AllowResizeUpdates(0)
        self.sr.browser.sr.window = self



    def LoadHTML(self, html, hideBackground = 0, newThread = 1):
        self.sr.browser.sr.hideBackground = hideBackground
        self.sr.browser.LoadHTML(html, newThread=newThread)



    def OnEndScale_(self, *args):
        self.reloadedScaleSize = (self.width, self.height)
        uthread.new(self.Reload, 0)



    def Reload(self, forced = 1, *args):
        if not self or self.destroyed:
            return 
        url = self.sr.browser.sr.currentURL
        if url and forced:
            uthread.new(self.GoTo, url, self.sr.browser.sr.currentData, scrollTo=self.sr.browser.GetScrollProportion())
        else:
            uthread.new(self.sr.browser.LoadHTML, None, scrollTo=self.sr.browser.GetScrollProportion())




