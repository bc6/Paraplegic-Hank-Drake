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
import uiutil
import localization
import localizationUtil
globals().update(service.consts)

class Agents(service.Service):
    __exportedcalls__ = {'InteractWith': [],
     'RemoteNamePopup': [ROLE_SERVICE],
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
    __notifyevents__ = ['OnAgentMissionChange',
     'OnSessionChanged',
     'OnInteractWith',
     'ProcessUIRefresh']

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



    def GetDivisions(self):
        if self.divisions is None:
            self.divisions = sm.RemoteSvc('corporationSvc').GetNPCDivisions().Index('divisionID')
            for row in self.divisions.values():
                row.divisionName = localization.GetByMessageID(row.divisionNameID)
                row.leaderType = localization.GetByMessageID(row.leaderTypeID)

        return self.divisions



    def __init__(self):
        service.Service.__init__(self)
        self.windows = {}
        self.allAgents = None
        self.divisions = None
        self.agentMonikers = {}
        self.lastMonikerAccess = blue.os.GetWallclockTime()
        uthread.worker('agents::ClearMonikers', self._Agents__ClearAgentMonikers)



    def GetAgentMoniker(self, agentID):
        if agentID not in self.agentMonikers:
            if getattr(self, 'allAgentsByID', False) and agentID in self.allAgentsByID and self.allAgentsByID[agentID].stationID:
                self.agentMonikers[agentID] = moniker.GetAgent(agentID, self.allAgentsByID[agentID].stationID)
            else:
                self.agentMonikers[agentID] = moniker.GetAgent(agentID)
        self.lastMonikerAccess = blue.os.GetWallclockTime()
        return self.agentMonikers[agentID]



    def __ClearAgentMonikers(self):
        while self.state == service.SERVICE_RUNNING:
            blue.pyos.synchro.SleepWallclock(300000)
            if blue.os.GetWallclockTime() > self.lastMonikerAccess + 30 * MIN:
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
            rejectMessage = localization.GetByLabel('UI/Agents/StandardMissionCargoCapWarning', cargoUnits=mandatoryCargoUnits)
            self.MessageBox(localization.GetByLabel('UI/Agents/CannotAcceptMission'), rejectMessage)
            return ('mission.offeredinsufficientcargospace', rejectMessage)
        if capacity - (used + cargoUnits) < 0:
            if capacity - (used + cargoUnits) < 1:
                c1 = cargoUnits
                c2 = capacity - used
            else:
                c1 = cargoUnits
                c2 = capacity - used
            if not self.YesNo(localization.GetByLabel('UI/Agents/CargoCapacityWarning'), localization.GetByLabel('UI/Agents/StandardMissionAcceptCargoCapWarning', requiredUnits=c1, availableUnits=c2), 'AgtMissionAcceptBigCargo'):
                return 'mission.offered'



    def YesNo(self, title, body, suppressID = None):
        if type(title) is tuple:
            titleText = localization.GetByLabel(title[0], **title[1])
        else:
            titleText = title
        if type(body) is tuple:
            bodyText = localization.GetByLabel(body[0], **body[1])
        else:
            bodyText = body
        options = {'text': bodyText,
         'title': titleText,
         'buttons': uiconst.YESNO,
         'icon': uiconst.QUESTION}
        ret = self.ShowMessageWindow(options, suppressID)
        return ret == uiconst.ID_YES



    def MessageBox(self, title, body, suppressID = None):
        if type(title) is tuple:
            titleText = localization.GetByLabel(title[0], **title[1])
        else:
            titleText = title
        if type(body) is tuple:
            bodyText = localization.GetByLabel(body[0], **body[1])
        else:
            bodyText = body
        options = {'text': bodyText,
         'title': titleText,
         'buttons': triui.OK,
         'icon': triui.INFO}
        self.ShowMessageWindow(options, suppressID)



    def ShowMessageWindow(self, options, suppressID = None):
        if suppressID:
            supp = settings.user.suppress.Get('suppress.' + suppressID, None)
            if supp is not None:
                return supp
            options['suppText'] = localization.GetByLabel('UI/Common/SuppressionShowMessage')
        (ret, block,) = sm.StartService('gameui').MessageBox(**options)
        if suppressID and block and ret not in [uiconst.ID_NO]:
            settings.user.suppress.Set('suppress.' + suppressID, ret)
        return ret



    def SingleChoiceBox(self, title, body, choices, suppressID = None):
        if type(title) is tuple:
            titleText = localization.GetByLabel(title[0], **title[1])
        else:
            titleText = title
        if type(body) is tuple:
            bodyText = localization.GetByLabel(body[0], **body[1])
        else:
            bodyText = body
        choicesText = []
        for choice in choices:
            if type(choice) is tuple:
                choicesText.append(localization.GetByLabel(choice[0], **choice[1]))
            else:
                choicesText.append(choice)

        options = {'text': bodyText,
         'title': titleText,
         'icon': triui.QUESTION,
         'buttons': uiconst.OKCANCEL,
         'radioOptions': choicesText}
        if suppressID:
            supp = settings.user.suppress.Get('suppress.' + suppressID, None)
            if supp is not None:
                return supp
            options['suppText'] = localization.GetByLabel('UI/Common/SuppressionShowMessageRemember')
        (ret, block,) = sm.StartService('gameui').RadioButtonMessageBox(**options)
        if suppressID and block:
            settings.user.suppress.Set('suppress.' + suppressID, ret)
        return (ret[0] == uiconst.ID_OK, ret[1])



    def GetQuantity(self, **keywords):
        ret = uix.QtyPopup(**keywords)
        if not ret:
            return None
        return ret.get('qty', None)



    def RemoteNamePopup(self, caption, label):
        if type(caption) is tuple:
            captionText = localization.GetByLabel(caption[0], **caption[1])
        else:
            captionText = caption
        if type(label) is tuple:
            labelText = localization.GetByLabel(label[0], **label[1])
        else:
            labelText = label
        ret = uix.NamePopup(captionText, labelText)
        if ret is not None:
            return ret['name']
        else:
            return 



    def PopupSelect(self, title, explanation, **keywords):
        if type(title) is tuple:
            titleText = localization.GetByLabel(title[0], **title[1])
        else:
            titleText = title
        if type(explanation) is tuple:
            explanationText = localization.GetByLabel(explanation[0], **explanation[1])
        else:
            explanationText = explanation
        if 'typeIDs' in keywords:
            displayList = []
            for typeID in keywords['typeIDs']:
                displayList.append([cfg.invtypes.Get(typeID).name, typeID, typeID])

            ret = uix.ListWnd(displayList, 'type', titleText, explanationText, 0, 300)
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



    def ProcessUIRefresh(self):
        if not getattr(self, 'divisions', None):
            return 
        for row in self.divisions.values():
            row.divisionName = localization.GetByMessageID(row.divisionNameID)
            row.leaderType = localization.GetByMessageID(row.leaderTypeID)

        for agentID in self.windows:
            state = self.windows[agentID].state
            self.windows[agentID].Close()
            self.InteractWith(agentID)
            self.windows[agentID].SetState(state)




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
                if dlg == const.agentDialogueButtonLocateCharacter:
                    agentHasLocatorService = True

            isResearchAgent = False
            if self.GetAgentByID(wnd.sr.agentID).agentTypeID == const.agentTypeResearchAgent:
                isResearchAgent = True
            if firstActionDialogue == const.agentDialogueButtonRequestMission and not agentHasLocatorService and not isResearchAgent:
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
                    window.Close()
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
                    window.Close()
                else:
                    self.PopupMissionJournal(agentID)
        if agentID in self.windows:
            agentDialogueWindow = self.windows[agentID]
            if what in (const.agentMissionDeclined, const.agentMissionQuit) and 'objectiveBrowser' in agentDialogueWindow.htmlCache:
                del agentDialogueWindow.htmlCache['objectiveBrowser']
            if what in (const.agentMissionOfferRemoved, const.agentMissionReset, const.agentTalkToMissionCompleted):
                if not agentDialogueWindow.destroyed:
                    agentDialogueWindow.CloseByUser()
                del self.windows[agentID]



    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid2' in change:
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
                    browser = form.AgentBrowser.Open(caption=localization.GetByLabel('UI/Agents/MissionJournalWithAgent', agentID=agentID))
                    self.journalwindows[(agentID, 'mission')] = browser
                else:
                    browser = self.journalwindows[(agentID, 'mission')]
                browser.SetMinSize([420, 400])
                uthread.new(self.LoadPage, browser, html, popup)

        finally:
            self.reentrancyGuard2 = 0




    def PopupDungeonShipRestrictionList(self, agentID, charID = None, dungeonID = None):
        restrictions = self.GetAgentMoniker(agentID).GetDungeonShipRestrictions(dungeonID)
        title = localization.GetByLabel('UI/Agents/Dialogue/DungeonShipRestrictionsHeader')
        ship = None
        shipID = util.GetActiveShip()
        if shipID is not None:
            ship = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItem(shipID)
        shipGroupID = shipTypeID = None
        body = ''
        if ship:
            shipGroupID = getattr(ship, 'groupID', None)
            shipTypeID = ship.typeID
        if shipGroupID:
            if shipGroupID in restrictions.restrictedShipTypes:
                msgPath = 'UI/Agents/Dialogue/DungeonShipRestrictionsListShipIsRestricted'
            elif shipGroupID in restrictions.allowedShipTypes:
                if len(restrictions.allowedShipTypes) > 1:
                    msgPath = 'UI/Agents/Dialogue/DungeonShipRestrictionsListShipIsNotRestricted'
                else:
                    restrictions.allowedShipTypes.remove(shipGroupID)
                    body = localization.GetByLabel('UI/Agents/Dialogue/DungeonShipRestrictionShipIsNotRestricted', groupName=cfg.invgroups.Get(shipGroupID).groupName, typeID=shipTypeID)
        else:
            msgPath = 'UI/Agents/Dialogue/DungeonShipRestrictionsShowList'
        if len(restrictions.allowedShipTypes) > 0:
            permittedShipGroupList = []
            for shipGroupID in restrictions.allowedShipTypes:
                permittedShipGroupList.append(cfg.invgroups.Get(shipGroupID).groupName)

            localizationUtil.Sort(permittedShipGroupList)
            shipList = ''
            for each in permittedShipGroupList:
                shipList += u'  \u2022' + each + '<br>'

            body = localization.GetByLabel(msgPath, shipTypeID=shipTypeID, shipList=shipList)
        options = {'text': body,
         'title': title,
         'buttons': triui.OK,
         'icon': triui.INFO}
        self.ShowMessageWindow(options)



    def RemoveOfferFromJournal(self, agentID):
        self.GetAgentMoniker(agentID).RemoveOfferFromJournal()



    def OpenAgentDialogueWindow(self, windowName = 'agentDialogueWindow', agentID = None):
        window = form.AgentDialogueWindow.Open(windowID=windowName, agentID=agentID)
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
                    browser = form.AgentBrowser(caption=localization.GetByLabel('UI/Agents/MissionJournalWithAgent', agentID=agentID))
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
                secWarning = localization.GetByLabel('UI/Agents/Dialogue/AutopilotRouteNotFound')
                break
            elif len(route) > 0:
                routeStart = route[(len(route) - 1)]
                for solarsystem in route:
                    s = sm.GetService('map').GetItem(solarsystem)
                    if charSecStatus > -5.0 and sm.StartService('map').GetSecurityClass(solarsystem) <= const.securityClassLowSec:
                        secWarning = localization.GetByLabel('UI/Agents/Dialogue/AutopilotRouteLowSecWarning')
                        break
                    elif charSecStatus < -5.0 and sm.StartService('map').GetSecurityClass(solarsystem) == const.securityClassHighSec:
                        secWarning = localization.GetByLabel('UI/Agents/Dialogue/AutopilotRouteHighSecWarning')
                        break


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


    _buttonLabelMapping = {const.agentDialogueButtonViewMission: 'UI/Agents/Dialogue/Buttons/ViewMission',
     const.agentDialogueButtonRequestMission: 'UI/Agents/Dialogue/Buttons/RequestMission',
     const.agentDialogueButtonAccept: 'UI/Agents/Dialogue/Buttons/AcceptMission',
     const.agentDialogueButtonAcceptChoice: 'UI/Agents/Dialogue/Buttons/AcceptThisChoice',
     const.agentDialogueButtonAcceptRemotely: 'UI/Agents/Dialogue/Buttons/AcceptRemotely',
     const.agentDialogueButtonComplete: 'UI/Agents/Dialogue/Buttons/CompleteMission',
     const.agentDialogueButtonCompleteRemotely: 'UI/Agents/Dialogue/Buttons/CompleteRemotely',
     const.agentDialogueButtonContinue: 'UI/Agents/Dialogue/Buttons/Continue',
     const.agentDialogueButtonDecline: 'UI/Agents/Dialogue/Buttons/DeclineMission',
     const.agentDialogueButtonDefer: 'UI/Agents/Dialogue/Buttons/DeferMission',
     const.agentDialogueButtonQuit: 'UI/Agents/Dialogue/Buttons/QuitMission',
     const.agentDialogueButtonStartResearch: 'UI/Agents/Dialogue/Buttons/StartResearch',
     const.agentDialogueButtonCancelResearch: 'UI/Agents/Dialogue/Buttons/CancelResearch',
     const.agentDialogueButtonBuyDatacores: 'UI/Agents/Dialogue/Buttons/BuyDatacores',
     const.agentDialogueButtonLocateCharacter: 'UI/Agents/Dialogue/Buttons/LocateCharacter',
     const.agentDialogueButtonLocateAccept: 'UI/Agents/Dialogue/Buttons/LocateCharacterAccept',
     const.agentDialogueButtonLocateReject: 'UI/Agents/Dialogue/Buttons/LocateCharacterReject',
     const.agentDialogueButtonYes: 'UI/Common/Buttons/Yes',
     const.agentDialogueButtonNo: 'UI/Common/Buttons/No'}

    def GetLabelForButtonID(self, buttonID):
        return self._buttonLabelMapping.get(buttonID, '')



    def __Interact(self, agentDialogueWindow, actionID = None, closeWindowAfterInteraction = False):
        if actionID:
            agentDialogueWindow.DisableButtons()
        (agentSays, dialogue, extraInfo,) = self._Agents__GetConversation(agentDialogueWindow, actionID)
        briefingInformation = self.GetMissionBriefingInformation(agentDialogueWindow)
        initialContentID = None
        if agentSays is None:
            return 
        if closeWindowAfterInteraction:
            agentDialogueWindow.CloseByUser()
            return 
        if extraInfo.get('missionQuit', None):
            agentDialogueWindow.CloseByUser()
            return 
        customAgentButtons = {'okLabel': [],
         'okFunc': [],
         'args': []}
        disabledButtons = []
        charSays = ''
        extraMissionInfo = ''
        numDialogChoices = 0
        isAgentInteractionMission = False
        appendCloseButton = False
        adminBlock = ''
        if dialogue:
            adminOptions = []
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
                elif type(each[1]) is int:
                    labelPath = self.GetLabelForButtonID(each[1])
                    if labelPath:
                        label = localization.GetByLabel(labelPath)
                    else:
                        self.LogError('Unknown button ID for agent action, id =', each[1])
                        label = 'Unknown ID ' + str(each[1])
                    closeWindowOnClick = each[1] == const.agentDialogueButtonDefer
                    if each[1] in (const.agentDialogueButtonRequestMission,
                     const.agentDialogueButtonContinue,
                     const.agentDialogueButtonQuit,
                     const.agentDialogueButtonCancelResearch):
                        appendCloseButton = True
                    customAgentButtons['okLabel'].append(label)
                    customAgentButtons['okFunc'].append(self.DoAction)
                    customAgentButtons['args'].append((agentDialogueWindow.sr.agentID, each[0], closeWindowOnClick))
                else:
                    adminOptions.append('<a href="localsvc:service=agents&method=DoAction&agentID=%d&actionID=%d">%s</a>' % (agentDialogueWindow.sr.agentID, each[0], each[1]))

            if adminOptions:
                if len(adminOptions) == 1:
                    adminBlock = '<TR><TD align=center><BR>'
                    adminBlock += adminOptions[0]
                else:
                    adminBlock = '<TR><TD>'
                    adminBlock += '<OL>'
                    adminBlock += ''.join([ '<BR><LI>%s</LI>' % x for x in adminOptions ])
                    adminBlock += '</OL>'
                adminBlock += '</TR></TD>'
        a = self.GetAgentByID(agentDialogueWindow.sr.agentID)
        agentCorpID = a.corporationID
        agentDivisionID = a.divisionID
        s = [sm.GetService('standing').GetEffectiveStanding(a.factionID, eve.session.charid)[0], sm.GetService('standing').GetEffectiveStanding(a.corporationID, eve.session.charid)[0], sm.GetService('standing').GetEffectiveStanding(a.agentID, eve.session.charid)[0]]
        if min(*s) <= -2.0:
            blurbEffectiveStanding = localization.GetByLabel('UI/Agents/Dialogue/EffectiveStandingLow', effectiveStanding=min(*s))
        else:
            es = max(*s) or 0.0
            blurbEffectiveStanding = localization.GetByLabel('UI/Agents/Dialogue/EffectiveStanding', effectiveStanding=es)
        lp = getattr(agentDialogueWindow.sr, 'oob', {}).get('loyaltyPoints', 0)
        if lp:
            loyaltyPoints = localization.GetByLabel('UI/Agents/Dialogue/LoyaltyPointsTableRow', loyaltyPoints=lp)
        else:
            loyaltyPoints = ''
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
            blurbEffectiveStanding = ''
            blurbDivision = ''
        else:
            agentInfoIcon = '<a href=showinfo:%d//%d><img src=icon:38_208 size=16 alt="%s"></a>' % (self.GetAgentInventoryTypeByBloodline(a.bloodlineID), a.agentID, uiutil.StripTags(localization.GetByLabel('UI/Commands/ShowInfo'), stripOnly=['localized']))
            divisions = self.GetDivisions()
            blurbDivision = localization.GetByLabel('UI/Agents/Dialogue/Division', divisionName=divisions[agentDivisionID].divisionName)
        agentLocationWrap = self.GetAgentMoniker(agentDialogueWindow.sr.agentID).GetAgentLocationWrap()
        bodyProps = {'agentID': agentDialogueWindow.sr.agentID,
         'agentName': cfg.eveowners.Get(agentDialogueWindow.sr.agentID).name,
         'showInfoLink': agentInfoIcon,
         'blurbDivision': blurbDivision,
         'agentLocation': agentLocationWrap,
         'blurbEffectiveStanding': blurbEffectiveStanding,
         'loyaltyPoints': loyaltyPoints,
         'missionTitle': missionTitle,
         'agentSays': agentSays,
         'extraMissionInfo': extraMissionInfo,
         'adminBlock': adminBlock}
        body = '\n<HTML>\n<HEAD>\n<LINK REL="stylesheet" TYPE="text/css" HREF="res:/ui/css/agentconvo.css">\n</HEAD>\n<BODY background-color=#00000000 link=#FFA800>\n    <TABLE border=0 cellpadding=1 cellspacing=1>\n        <TR>\n            <TD valign=top >\n                <TABLE border=0 cellpadding=1 cellspacing=1>\n                    <TR>\n                    </TR>\n                    <TR>\n                    </TR>\n                    <TR>\n                    </TR>\n                    <TR>\n                        <TD valign=top><img src="portrait:%(agentID)d" width=120 height=120 size=256 align=left style=margin-right:10></TD>\n                    </TR>\n                </TABLE>\n            </TD>\n            <TD valign=top>\n                    <TABLE border=0 width=290 cellpadding=1 cellspacing=1>\n                    <TR>\n                        <TD width=120 valign=top colspan=2><font size=24>%(agentName)s</font> \n                        %(showInfoLink)s\n                        </TD>\n                    </TR>\n                    <TR>\n                        <TD>%(blurbDivision)s</TD>\n                    </TR>\n                    <TR>\n                        <TD height=12> </TD>\n                    </TR>\n                    <TR>\n                        <TD>%(agentLocation)s</TD>\n                    </TR>\n                    <TR>\n                        <TD height=12> </TD>\n                    </TR>\n                    <TR>\n                        <TD>%(blurbEffectiveStanding)s</TD>\n                    </TR>\n                    %(loyaltyPoints)s\n                </TABLE>\n            </TD>\n        </TR>\n    </TABLE>\n\n    <table width=380 cellpadding=2>\n    <tr>\n        <td>\n            %(missionTitle)s\n            <div id=basetext><font size=12>%(agentSays)s</font></div>\n        </td>\n    </tr>\n    </table>\n    <TABLE width="380">\n        <TR>\n            <TD>\n                %(extraMissionInfo)s\n            </TD>\n        </TR>\n        %(adminBlock)s\n    </TABLE>\n</BODY>\n</HTML>\n    '
        html = body % bodyProps
        if self.printHTML:
            print '-----------------------------------------------------------------------------------'
            print html
            print '-----------------------------------------------------------------------------------'
        numButtons = len(customAgentButtons['okLabel'])
        if appendCloseButton and numButtons < 3:
            customAgentButtons['okLabel'].append(localization.GetByLabel('UI/Common/Buttons/Close'))
            customAgentButtons['okFunc'].append(agentDialogueWindow.CloseByUser)
            customAgentButtons['args'].append('self')
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



    def ProcessAgentInfoKeyVal(self, data):
        infoFunc = {'research': self._ProcessResearchServiceInfo,
         'locate': self._ProcessLocateServiceInfo,
         'mission': self._ProcessMissionServiceInfo}.get(data.agentServiceType, None)
        if infoFunc:
            return infoFunc(data)
        else:
            return []



    def _ProcessResearchServiceInfo(self, data):
        header = localization.GetByLabel('UI/Agents/Research/ResearchServices', session.languageID)
        skillList = []
        for (skillTypeID, skillLevel,) in data.skills:
            skillList.append(localization.GetByLabel('UI/Agents/Research/SkillListing', session.languageID, skillID=skillTypeID, skillLevel=skillLevel))

        if not skillList:
            skills = localization.GetByLabel('UI/Agents/Research/ErrorNoRelevantResearchSkills', session.languageID)
        else:
            skillList = localizationUtil.Sort(skillList)
            skills = localizationUtil.FormatGenericList(skillList)
        details = [(localization.GetByLabel('UI/Agents/Research/RelevantSkills', session.languageID), skills)]
        status = []
        if data.researchData:
            researchData = data.researchData
            researchStuff = [(localization.GetByLabel('UI/Agents/Research/ResearchField', session.languageID), cfg.invtypes.Get(researchData['skillTypeID']).name), (localization.GetByLabel('UI/Agents/Research/CurrentStatus', session.languageID), localization.GetByLabel('UI/Agents/Research/CurrentStatusRP', session.languageID, rpAmount=researchData['points'])), (localization.GetByLabel('UI/Agents/Research/ResearchRate', session.languageID), localization.GetByLabel('UI/Agents/Research/ResearchRateRPDay', session.languageID, rpAmount=researchData['pointsPerDay']))]
            rpMultiplier = researchData['rpMultiplier']
            if rpMultiplier > 1:
                researchStuff.append((localization.GetByLabel('UI/Agents/Research/ResearchFieldBonus', session.languageID), localization.GetByLabel('UI/Agents/Research/ResearchFieldBonusRPMultiplier', session.languageID, rpMultiplier=rpMultiplier)))
            status = [(localization.GetByLabel('UI/Agents/Research/YourResearch', session.languageID), researchStuff)]
        research = []
        for (skillTypeID, pattentIDs,) in data.researchSummary:
            predictablePatentNames = []
            for blueprintTypeID in pattentIDs:
                predictablePatentNames.append(cfg.invtypes.Get(blueprintTypeID).name)

            if predictablePatentNames:
                predictablePatentNames = localizationUtil.Sort(predictablePatentNames)
                predictablePatents = localizationUtil.FormatGenericList(predictablePatentNames)
            else:
                predictablePatents = localization.GetByLabel('UI/Agents/Research/NoPredictablePatents', session.languageID)
            research.append((localization.GetByLabel('UI/Agents/Research/ResearchSummary', session.languageID, skillTypeID=skillTypeID), [(localization.GetByLabel('UI/Agents/Research/PredictablePatents', session.languageID), predictablePatents)]))

        return [(header, details)] + status + research



    def _ProcessLocateServiceInfo(self, data):
        header = localization.GetByLabel('UI/Agents/Locator/LocationServices', session.languageID)
        if data.frequency:
            details = [(localization.GetByLabel('UI/Agents/Locator/MaxFrequency', session.languageID), localization.GetByLabel('UI/Agents/Locator/EveryInterval', session.languageID, interval=data.frequency))]
        else:
            details = [(localization.GetByLabel('UI/Agents/Locator/MaxFrequency', session.languageID), localization.GetByLabel('UI/Generic/NotAvailableShort', session.languageID))]
        for (delayRange, delay, cost,) in data.delays:
            rangeText = [localization.GetByLabel('UI/Agents/Locator/SameSolarSystem', session.languageID),
             localization.GetByLabel('UI/Agents/Locator/SameConstellation', session.languageID),
             localization.GetByLabel('UI/Agents/Locator/SameRegion', session.languageID),
             localization.GetByLabel('UI/Agents/Locator/DifferentRegion', session.languageID)][delayRange]
            if not delay:
                delay = localization.GetByLabel('UI/Agents/Locator/ResultsInstantaneous', session.languageID)
            else:
                delay = util.FmtTimeInterval(delay * SEC)
            details.append((rangeText, localizationUtil.FormatGenericList((util.FmtISK(cost), delay))))

        if data.callbackID:
            details.append((localization.GetByLabel('UI/Agents/Locator/Availability', session.languageID), localization.GetByLabel('UI/Agents/Locator/NotAvailableInProgress', session.languageID)))
        elif data.lastUsed and blue.os.GetWallclockTime() - data.lastUsed < data.frequency:
            details.append((localization.GetByLabel('UI/Agents/Locator/AvailableAgain', session.languageID), util.FmtDate(data.lastUsed + data.frequency)))
        return [(header, details)]



    def _ProcessMissionServiceInfo(self, data):
        if data.available:
            return [(localization.GetByLabel('UI/Agents/MissionServices', session.languageID), [(localization.GetByLabel('UI/Agents/MissionAvailability', session.languageID), localization.GetByLabel('UI/Agents/MissionAvailabilityStandard', session.languageID))])]
        else:
            return [(localization.GetByLabel('UI/Agents/MissionServices', session.languageID), [(localization.GetByLabel('UI/Agents/MissionAvailability', session.languageID), localization.GetByLabel('UI/Agents/MissionAvailabilityNone', session.languageID))])]




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




