import service
import uix
import uiutil
import uiconst
import uthread
import util
import blue
import form
import sys
import listentry
import uicls
import tutorial
import log
import geo2
from collections import defaultdict
import audio2
import localization
BLUETIME_TO_SECONDS = 10000000.0

def _ProximityCallBack(tutorialID, entidList):
    if session.charid not in entidList:
        return 
    sm.GetService('tutorial').OpenTutorialSequence_Check(tutorialID)



class TutorialSvc(service.Service):
    __guid__ = 'svc.tutorial'
    __update_on_reload__ = 0
    __exportedcalls__ = {'OpenTutorial': [service.ROLE_IGB],
     'OpenTutorialSequence_Check': [service.ROLE_IGB]}
    __notifyevents__ = ['OnSessionChanged', 'OnClearTutorialCache', 'OnServerTutorialRequest']
    __dependencies__ = ['settings']
    __componentTypes__ = ['proximityOpenTutorial']

    def __init__(self):
        service.Service.__init__(self)
        self.criterias = None
        self.actions = None
        self.categories = None
        self.loadingTutorial = 0
        self.tutorials = None
        self.tutorialConnections = None
        self.tutorialInfos = {}
        self.sequences = {}
        self.waiting = None
        self.goodieIcons = None
        self.oldHeight = None
        self.waitingForWarpConfirm = False
        self.uiPointerSvc = None
        self.pageTime = blue.os.GetWallclockTime()
        self.careerAgents = {}
        self.tutorialNoob = True



    def Run(self, *etc):
        self.LogInfo('Starting Tutorial Service')
        service.Service.Run(self, *etc)
        self.uiPointerSvc = sm.StartService('uipointerSvc')
        self.audioEmitter = audio2.AudEmitter('Tutorial Audio')
        self.LogPageCompletion = None



    def Stop(self, memStream = None):
        if not sm.IsServiceRunning('window'):
            return 
        tutorialBrowser = self.GetTutorialBrowser(create=0)
        if tutorialBrowser:
            tutorialBrowser.CloseByUser()
        else:
            self.Cleanup()
        self.LogInfo('Stopping Tutorial Service')



    def Cleanup(self):
        self.audioEmitter.SendEvent(u'fade_out')
        self.uiPointerSvc.ClearPointers()
        eve.SetRookieState(None)



    def CreateComponent(self, name, state):
        component = tutorial.ProximityOpenTutorialComponent()
        component.tutorialID = int(state.get('tutorialID', None))
        component.radius = float(state.get('radius', None))
        return component



    def SetupComponent(self, entity, component):
        posComponent = entity.GetComponent('position')
        sm.GetService('proximity').AddCallbacks(instanceID=entity.scene.sceneID, pos=posComponent.position, range=component.radius, msToCheck=250, onEnterCallback=_ProximityCallBack, onExitCallback=lambda tutorialID, entidList: None, callbackArgs=component.tutorialID)



    def PackUpForClientTransfer(self, component):
        state = {}
        state['tutorialID'] = component.tutorialID
        state['radius'] = component.radius
        return state



    def PackUpForSceneTransfer(self, component, destinationSceneID = None):
        return self.PackUpForClientTransfer(component)



    def UnPackFromSceneTransfer(self, component, entity, state):
        component.tutorialID = state['tutorialID']
        component.radius = state['radius']
        return component



    def GetSequenceDoneStatus(self, sequenceID):
        return settings.char.ui.Get('SequenceDoneStatus', {}).get(sequenceID, (None, None))



    def SetSequenceDoneStatus(self, sequenceID, tutorialID, pageNo):
        stat = settings.char.ui.Get('SequenceDoneStatus', {})
        if tutorialID is None:
            del stat[sequenceID]
        else:
            stat[sequenceID] = (tutorialID, pageNo)
        settings.char.ui.Set('SequenceDoneStatus', stat)



    def GetSequenceStatus(self, sequenceID):
        return settings.char.ui.Get('SequenceStatus', {}).get(sequenceID, None)



    def SetSequenceStatus(self, sequenceID, tutorialID, pageNo, status = None):
        tutorialBrowser = self.GetTutorialBrowser(create=0)
        if tutorialBrowser and hasattr(tutorialBrowser, 'startTime'):
            time = (blue.os.GetWallclockTime() - tutorialBrowser.startTime) / 10000000
        else:
            time = 0
        stat = settings.char.ui.Get('SequenceStatus', {})
        if status == 'reset' and sequenceID in stat:
            tutorialBrowser = self.GetTutorialBrowser()
            tutorialBrowser.Close()
            self.uiPointerSvc.ClearPointers()
            if eve.session.solarsystemid2 and tutorialID != uix.tutorial:
                sm.GetService('neocom').StopAllBlink()
            if eve.session.stationid:
                lobby = form.Lobby.GetIfOpen()
                if lobby:
                    lobby.StopAllBlinkButtons()
            del stat[sequenceID]
        elif status == 'done':
            stat[sequenceID] = 'done'
            sm.RemoteSvc('tutorialSvc').LogCompleted(tutorialID, pageNo, int(time))
        elif status == 'aborted':
            stat[sequenceID] = 'done'
            sm.RemoteSvc('tutorialSvc').LogAborted(tutorialID, pageNo, int(time))
        else:
            stat[sequenceID] = (tutorialID, pageNo)
        saveSettings = False
        if stat.get(sequenceID, '') == 'done':
            saveSettings = True
            if sequenceID == uix.tutorialTutorials:
                settings.user.ui.Delete('doIntroTutorial%s' % session.charid)
                stat[uix.tutorialWorldspaceNavigation] = 'done'
        settings.char.ui.Set('SequenceStatus', stat)
        if saveSettings:
            sm.GetService('settings').SaveSettings()



    def GetSequence(self, sequenceID):
        return self.sequences.get(sequenceID, [])



    def GetNextInSequence(self, current, sequenceID, direction = 1):
        seq = self.GetSequence(sequenceID)
        if current in seq:
            if direction == 1 and current != seq[-1]:
                return seq[(seq.index(current) + direction)]
            if direction == -1 and current != seq[0]:
                return seq[(seq.index(current) + direction)]



    def GetSequencePageNoAndPageCount(self, tutorialID, tutorialPageNo):
        seq = self.GetSequence(tutorialID)
        pageCount = 0
        pageNo = tutorialPageNo
        gotPages = 0
        for _tutorialID in seq:
            tutData = self.GetTutorialInfo(_tutorialID)
            if not tutData:
                continue
            pageCount += len(tutData.pages)
            if _tutorialID == tutorialID:
                gotPages = 1
            if not gotPages:
                pageNo += len(tutData.pages)

        return (pageNo, pageCount)



    def GetOtherRookieFilter(self, key):
        return {'defaultchannels': 28.5}.get(key.lower(), 1000)



    def GetStationRookieFilter(self, servicename):
        return -1
        return {'reprocessingplant': 5,
         'market': 7,
         'fitting': 8,
         'repairshop': 36,
         'insurance': 38,
         'lobbytabs': 39,
         'agents': 39,
         'medical': 39}.get(servicename.lower(), 1000)



    def GetNeocomRookieFilter(self, buttonname):
        return -1
        return {'ships': 2,
         'charactersheet': 3,
         'items': 4,
         'wallet': 6,
         'market': 7,
         'map': 9,
         'undock': 10,
         'channels': 29,
         'addressbook': 30,
         'assets': 34,
         'corporation': 37,
         'help': 38,
         'journal': 40}.get(buttonname.lower(), 1000)



    def GetShipuiRookieFilter(self, buttonname):
        return {localization.GetByLabel('UI/Commands/ZoomIn'): 21,
         localization.GetByLabel('UI/Commands/ResetCamera'): 21,
         localization.GetByLabel('UI/Commands/ZoomOut'): 21,
         localization.GetByLabel('UI/Generic/Autopilot'): 35,
         localization.GetByLabel('UI/Generic/Tactical'): 21,
         localization.GetByLabel('UI/Generic/Scanner'): 21,
         localization.GetByLabel('UI/Generic/Cargo'): 21}.get(buttonname, 1000)



    def GetTutorialsByCategory(self):
        tutorials = self.GetTutorials()
        byCategs = {}
        for (tutorialID, tutorialData,) in tutorials.iteritems():
            if tutorialData.categoryID not in byCategs:
                byCategs[tutorialData.categoryID] = []
            tutorialName = localization.GetByMessageID(tutorialData.tutorialNameID)
            byCategs[tutorialData.categoryID].append((tutorialName, tutorialData))

        for (k, v,) in byCategs.iteritems():
            byCategs[k] = uiutil.SortListOfTuples(v)

        return byCategs



    def GetValidTutorials(self, newbie = True):
        validTutorials = []
        for (categoryID, tutorials,) in self.GetTutorialsByCategory().iteritems():
            if categoryID is None:
                continue
            for tutorial in tutorials:
                validTutorials.append(tutorial.tutorialID)


        return validTutorials



    def OpenTutorialSequence_Check(self, tutorialID = None, force = 0, click = 0, pageNo = None):
        if force:
            settings.char.ui.Set('showTutorials', 1)
        if not settings.char.ui.Get('showTutorials', 1):
            return 
        if tutorialID not in self.GetValidTutorials():
            self.LogWarn('TutorialSvc: Attempting to open tutorial', tutorialID, 'which is not a valid tutorial ID')
            return 
        tutorialBrowser = self.GetTutorialBrowser(create=0)
        if not force and tutorialBrowser and getattr(tutorialBrowser, 'current', None):
            (_tutorialID, _pageNo, _pageID, _pageCount, _sequenceID, _VID, _pageActionID,) = tutorialBrowser.current
            if _sequenceID and not tutorialBrowser.done:
                return 
        seqStat = self.GetSequenceStatus(tutorialID)
        if seqStat == 'done' and force:
            stat = settings.char.ui.Get('SequenceStatus', {})
            if tutorialID in stat:
                del stat[tutorialID]
                settings.char.ui.Set('SequenceStatus', stat)
                seqStat = self.GetSequenceStatus(tutorialID)
        if seqStat == 'done':
            return 
        if tutorialID not in self.sequences:
            self.sequences[tutorialID] = []
            nextID = tutorialID
            tutorials = self.GetTutorials()
            while 1:
                if nextID in self.sequences[tutorialID]:
                    log.LogError('Cannot resolve the tutorial sequence, its in loop', tutorialID)
                    break
                self.sequences[tutorialID].append(nextID)
                nextID = self.GetNextTutorial(nextID)
                if not nextID:
                    break

        tid = tutorialID
        if seqStat and not force:
            (_tutorialID, pageNo,) = seqStat
            self.OpenTutorial(_tutorialID, pageNo, sequenceID=tutorialID, force=force, click=click)
            tid = _tutorialID
        else:
            self.OpenTutorial(tutorialID, pageNo=pageNo, sequenceID=tutorialID, force=force, click=click)



    def GetNextTutorial(self, tutorialID):
        tutorialConnections = self.GetTutorialConnections()
        if tutorialID in tutorialConnections:
            nextID = tutorialConnections[tutorialID].get(session.raceID, None)
            if not nextID:
                nextID = tutorialConnections[tutorialID].get(0, None)
            return nextID



    def GetTutorialBrowser(self, create = 1):
        tutorialBrowser = form.TutorialWindow.GetIfOpen()
        if not tutorialBrowser and create:
            tutorialBrowser = form.TutorialWindow.Open()
        if tutorialBrowser:
            tutorialBrowser.constrainScreen = True
            if tutorialBrowser.sr.stack is not None:
                tutorialBrowser.sr.stack.RemoveWnd(tutorialBrowser, 0, 0)
            if session.role & service.ROLE_GML == 0 and self.tutorialNoob:
                tutorialBrowser.MakeUnKillable()
                repairSysSkill = sm.GetService('skills').HasSkill(const.typeRepairSystems)
                shieldOpsSkill = sm.GetService('skills').HasSkill(const.typeShieldOperations)
                if repairSysSkill or shieldOpsSkill:
                    tutorialBrowser.MakeKillable()
        if tutorialBrowser and not getattr(tutorialBrowser.sr, 'bottom', None):
            tutorialBrowser.SetWndIcon('ui_74_64_13')
            tutorialBrowser.HideHeader()
            tutorialBrowser.ButtonBarOff()
            tutorialBrowser.StatusBarOff()
            tutorialBrowser.AddressBarOff()
            tutorialBrowser.OptionsOff()
            tutorialBrowser.MakeUnMinimizable()
            tutorialBrowser.MakeUnstackable()
            tutorialBrowser.SetMinSize([350, 220])
            tutorialBrowser._OnClose = self.OnCloseWnd
            tutorialBrowser.sr.imgpar = uicls.Container(name='imgpar', parent=uiutil.GetChild(tutorialBrowser, 'main'), align=uiconst.TOLEFT, width=64, idx=4, state=uiconst.UI_HIDDEN, clipChildren=1)
            imgparclipper = uicls.Container(name='imgparclipper', parent=tutorialBrowser.sr.imgpar, align=uiconst.TOALL, left=5, top=5, width=5, height=5, clipChildren=1)
            tutorialBrowser.sr.img = uicls.Sprite(parent=imgparclipper, align=uiconst.RELATIVE, left=1, top=1)
            uicls.Frame(parent=tutorialBrowser.sr.imgpar, color=(1.0, 1.0, 1.0, 0.25), padding=(4, 4, 4, 4))
            tutorialBrowser.sr.bottom = uicls.Container(name='bottom', parent=tutorialBrowser.sr.maincontainer, align=uiconst.TOBOTTOM, height=22, idx=0)
            tutorialBrowser.sr.back = uicls.Button(parent=tutorialBrowser.sr.bottom, label=localization.GetByLabel('UI/Commands/Back'), func=self.Back, pos=(3, 0, 0, 0))
            tutorialBrowser.sr.back.name = 'tutorialBackBtn'
            tutorialBrowser.sr.next = uicls.Button(parent=tutorialBrowser.sr.bottom, label=localization.GetByLabel('UI/Commands/Next'), func=self.Next, align=uiconst.TOPRIGHT, pos=(3, 0, 0, 0), btn_default=1)
            tutorialBrowser.Confirm = self.Next
            tutorialBrowser.sr.next.name = 'tutorialNextBtn'
            tutorialBrowser.sr.text = uicls.EveLabelMedium(text='', parent=tutorialBrowser.sr.bottom, state=uiconst.UI_DISABLED, align=uiconst.CENTER)
            tutorialBrowser.sr.browser.sr.activeframe.SetRGB(1.0, 1.0, 1.0, 0.0)
            uicls.Frame(parent=tutorialBrowser.sr.browser, color=(1.0, 1.0, 1.0, 0.25), padding=(-1, -1, -1, -1))
            top = tutorialBrowser.sr.tTop = uicls.Container(name='tTop', parent=tutorialBrowser.sr.topParent, align=uiconst.TOALL, padding=(64, 0, 64, 0), idx=0)
            tutorialBrowser.sr.captionText = uicls.Label(text='', parent=top, align=uiconst.TOTOP, fontsize=18, top=10, state=uiconst.UI_DISABLED, uppercase=1)
            tutorialBrowser.sr.captionText.mmbold = 0.75
            tutorialBrowser.sr.captionText.OnSizeChanged = self.CheckTopHeight
            tutorialBrowser.sr.subcaption = uicls.EveLabelMedium(text='', parent=top, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
            tutorialBrowser.sr.browser.AllowResizeUpdates(1)
            tutorialBrowser.SetParent(uicore.layer.abovemain)
        return tutorialBrowser



    def GetCategory(self, categoryID):
        if self.categories is None:
            self.categories = {}
            try:
                categories = sm.RemoteSvc('tutorialSvc').GetCategories()
                for category in categories:
                    self.categories[category.categoryID] = category
                    self.categories[category.categoryID].categoryName = localization.GetByMessageID(category.categoryNameID)
                    self.categories[category.categoryID].description = localization.GetByMessageID(category.descriptionID)

            except:
                sys.exc_clear()
        if categoryID in self.categories:
            return self.categories[categoryID]



    def GetCriteria(self, criteriaID):
        if self.criterias is None:
            self.criterias = {}
            try:
                criterias = sm.RemoteSvc('tutorialSvc').GetCriterias()
                for criteria in criterias:
                    self.criterias[criteria.criteriaID] = criteria

            except:
                sys.exc_clear()
        if criteriaID in self.criterias:
            return self.criterias[criteriaID]



    def GetAction(self, actionID):
        if self.actions is None:
            self.actions = {}
            actions = sm.RemoteSvc('tutorialSvc').GetActions()
            for action in actions:
                self.actions[action.actionID] = action

        if actionID in self.actions:
            return self.actions[actionID]



    def __PopulateTutorialsAndConnections(self):
        try:
            (t, tc,) = sm.RemoteSvc('tutorialSvc').GetTutorialsAndConnections()
            self.tutorials = t.Index('tutorialID')
            tc = tc.Filter('tutorialID')
            self.tutorialConnections = defaultdict(dict)
            for (tutID, rows,) in tc.iteritems():
                for each in rows:
                    self.tutorialConnections[tutID][each.raceID] = each.nextTutorialID


        except:
            sys.exc_clear()



    def GetTutorials(self):
        if self.tutorials is None:
            self._TutorialSvc__PopulateTutorialsAndConnections()
        return self.tutorials



    def GetTutorialConnections(self):
        if self.tutorialConnections is None:
            self._TutorialSvc__PopulateTutorialsAndConnections()
        return self.tutorialConnections



    def OnClearTutorialCache(self):
        self.tutorialInfos = {}



    def OnServerTutorialRequest(self, tutorialID):
        self.OpenTutorialSequence_Check(tutorialID, force=1)



    def GetTutorialInfo(self, tutorialID):
        if tutorialID in self.tutorialInfos:
            return self.tutorialInfos[tutorialID]
        try:
            tutData = sm.RemoteSvc('tutorialSvc').GetTutorialInfo(tutorialID)
        except KeyError:
            sys.exc_clear()
            return None
        self.tutorialInfos[tutorialID] = tutData
        return tutData



    def OnSessionChanged(self, isRemote, session, change):
        self.UnhideTutorialWindow()
        if 'charid' in change:
            (oldCharID, newCharID,) = change['charid']
            if newCharID is not None:
                self.GetCharacterTutorialState()
        funnel = form.CareerFunnelWindow.GetIfOpen()
        if funnel:
            if util.IsWormholeSystem(eve.session.solarsystemid):
                eve.Message('NoAgentsInWormholes')
                funnel.CloseByUser()
                return 
            funnel.RefreshEntries()



    def OnCloseApp(self):
        tutorialBrowser = self.GetTutorialBrowser(create=0)
        if tutorialBrowser and hasattr(tutorialBrowser, 'current') and hasattr(tutorialBrowser, 'startTime'):
            time = (blue.os.GetWallclockTime() - tutorialBrowser.startTime) / 10000000
            tutorialID = tutorialBrowser.current[0]
            pageNo = tutorialBrowser.current[1]
            if tutorialID is not None and pageNo is not None:
                sm.RemoteSvc('tutorialSvc').LogAppClosed(tutorialID, pageNo, int(time))



    def AskClose(self, openState = 0):
        tutorialBrowser = self.GetTutorialBrowser(create=0)
        if hasattr(tutorialBrowser, 'current'):
            (tutorialID, pageNo, pageID, pageCount, sequenceID, VID, pageActionID,) = tutorialBrowser.current
            if sequenceID:
                if hasattr(tutorialBrowser, 'startTime'):
                    time = (blue.os.GetWallclockTime() - tutorialBrowser.startTime) / 10000000
                else:
                    time = 0
                if not getattr(tutorialBrowser, 'done', 0):
                    ret = eve.Message('TutorialContinueLater', {}, uiconst.YESNOCANCEL)
                    if ret not in (uiconst.ID_YES, uiconst.ID_NO):
                        return 
                    if ret == uiconst.ID_YES:
                        self.SetSequenceStatus(sequenceID, tutorialID, pageNo)
                        sm.RemoteSvc('tutorialSvc').LogClosed(tutorialID, pageNo, int(time))
                    elif ret == uiconst.ID_NO:
                        self.SetSequenceStatus(sequenceID, tutorialID, pageNo, 'aborted')
                else:
                    self.SetSequenceStatus(sequenceID, tutorialID, pageNo, 'done')
        tutorialBrowser.Close()
        self.uiPointerSvc.ClearPointers()



    def OnCloseWnd(self, *args):
        uthread.new(self.Cleanup)



    def UnhideTutorialWindow(self):
        self.ChangeTutorialWndState(visible=True)



    def Reload(self, *args):
        tutorialBrowser = self.GetTutorialBrowser()
        self.ReloadTutorialBrowser(tutorialBrowser)



    def ReloadTutorialBrowser(self, tutorialBrowser):
        if hasattr(tutorialBrowser, 'current'):
            (tutorialID, pageNo, pageID, pageCount, sequenceID, VID, pageActionID,) = tutorialBrowser.current
            self.OpenTutorial(tutorialID, pageNo, pageID, sequenceID, 1, VID)



    def Back(self, *args):
        tutorialBrowser = self.GetTutorialBrowser()
        if hasattr(tutorialBrowser, 'current'):
            (tutorialID, pageNo, pageID, pageCount, sequenceID, VID, pageActionID,) = tutorialBrowser.current
            if pageNo is not None and pageNo > 1:
                pageNo -= 1
                self.OpenTutorial(tutorialID, pageNo, pageID, VID=VID, sequenceID=sequenceID, checkBack=1)
                return 
            if sequenceID:
                nextTutorialID = self.GetNextInSequence(tutorialID, sequenceID, [-1, 1][tutorialBrowser.reverseBack])
                if nextTutorialID:
                    self.OpenTutorial(nextTutorialID, [-1, None][tutorialBrowser.reverseBack], VID=VID, sequenceID=sequenceID, checkBack=1)
                    return 



    def Next(self, *args):
        tutorialBrowser = self.GetTutorialBrowser()
        if hasattr(tutorialBrowser, 'current'):
            (tutorialID, pageNo, pageID, pageCount, sequenceID, VID, pageActionID,) = tutorialBrowser.current
            if pageNo is not None:
                if self.LogPageCompletion is None:
                    self.LogPageCompletion = sm.GetService('infoGatheringSvc').GetEventIGSHandle(const.infoEventTutorialPageCompletion)
                timeSpent = (blue.os.GetWallclockTime() - self.pageTime) / BLUETIME_TO_SECONDS
                self.LogPageCompletion(itemID=eve.session.charid, itemID2=tutorialID, int_1=pageNo, float_1=timeSpent)
                if pageNo == 1:
                    if tutorialBrowser and hasattr(tutorialBrowser, 'startTime'):
                        time = (blue.os.GetWallclockTime() - tutorialBrowser.startTime) / 10000000
                    else:
                        time = 0
                    sm.RemoteSvc('tutorialSvc').LogStarted(tutorialID, pageNo, int(time))
                if pageNo == pageCount:
                    self.ExecutePageAction(pageActionID)
                    if sequenceID:
                        nextTutorialID = self.GetNextInSequence(tutorialID, sequenceID)
                        if nextTutorialID:
                            self.OpenTutorial(nextTutorialID, VID=VID, sequenceID=sequenceID)
                            return 
                    tutorialBrowser.CloseByUser()
                    return 
                self.ExecutePageAction(pageActionID)
                pageNo += 1
                self.OpenTutorial(tutorialID, pageNo, pageID, VID=VID, sequenceID=sequenceID)



    def ShowCareerFunnel(self):
        form.CareerFunnelWindow.Open()



    def ExecutePageAction(self, pageActionID):
        if pageActionID is None:
            return 
        if int(pageActionID) == const.tutorialPagesActionOpenCareerFunnel:
            if not util.IsWormholeSystem(eve.session.solarsystemid):
                self.ShowCareerFunnel()



    def GiveGoodies(self, tutorialID, pageID, pageNo):
        retVal = self.GiveTutorialGoodies(tutorialID, pageID, pageNo)
        if retVal is not None:
            stationName = cfg.evelocations.Get(retVal).name
            eve.Message('TutorialGoodiesNotEnoughSpaceInCargo', {'stationName': stationName})



    def SlashCmd(self, slash):
        split = slash.split(' ')
        try:
            (VID, pageNo,) = (int(split[1]), int(split[2]))
        except:
            log.LogError('Failed to resolve slash command data:', slash, 'Usage: /tutorial <tutvid> <pageno>')
            sys.exc_clear()
            return 
        self.OpenTutorial(pageNo=pageNo, force=1, VID=VID, skipCriteria=True)



    def IsShipWarping(self):
        import destiny
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return 
        else:
            ship = bp.GetBall(eve.session.shipid)
            if ship is None:
                return 
            if ship.mode == destiny.DSTBALL_WARP:
                return True
            return False



    def __WarpToTutorial(self):
        errMsg = 'TutYouAreNotInANewbieSystem'
        if util.IsNewbieSystem(eve.session.solarsystemid2):
            if self.Precondition_Checkballpark('groupCloud') or self.IsShipWarping():
                return (1, None)
            self.ShowWarpToButton()
            return (1, None)
        return (2, errMsg)



    def ShowWarpToButton(self):
        browser = self.GetTutorialBrowser()
        self.waitingForWarpConfirm = True
        browser.sr.next.state = uiconst.UI_NORMAL
        browser.sr.next.OnClick = self.WarpToBallpark
        browser.sr.next.SetLabel(localization.GetByLabel('UI/Commands/WarpTo'))
        browser.sr.text.text = ''



    def WarpToBallpark(self, *args):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is None:
            raise RuntimeError('Remote park could not be retrieved.')
        bp.WarpToStuff('tutorial', None)
        self.waitingForWarpConfirm = False
        self.RevertWarpToButton()



    def RevertWarpToButton(self):
        browser = self.GetTutorialBrowser()
        browser.sr.next.state = uiconst.UI_NORMAL
        browser.sr.next.OnClick = self.Reload
        browser.sr.next.SetLabel(localization.GetByLabel('UI/Commands/Next'))
        browser.sr.text.text = ''



    def GiveTutorialGoodies(self, tutorialID, pageID, pageNo):
        return sm.RemoteSvc('tutorialLocationSvc').GiveTutorialGoodies(tutorialID, pageID, pageNo)



    def OpenTutorial(self, tutorialID = None, pageNo = None, pageID = None, sequenceID = None, force = 0, VID = None, skipCriteria = False, checkBack = 0, click = 0):
        self.pageTime = blue.os.GetWallclockTime()
        tutorialBrowser = self.GetTutorialBrowser()
        if self.loadingTutorial and tutorialBrowser:
            return 
        c = getattr(tutorialBrowser, 'current', None)
        if not force and c and c[0] == tutorialID and c[1] == pageNo and c[2] == pageID:
            self.loadingTutorial = 0
            return 
        self.loadingTutorial = 1
        try:
            tutorialBrowser.sr.back.state = uiconst.UI_HIDDEN
            tutorialBrowser.sr.next.state = uiconst.UI_HIDDEN
            tutorialBrowser.sr.back.Blink(0)
            tutorialBrowser.sr.next.Blink(0)
            tutorialBrowser.sr.text.text = ''
            tutorialBrowser.done = 0
            tutorialBrowser.reverseBack = 0
            imagePath = None
            pageCount = None
            body = '\n                <html>\n                <head>\n                <LINK REL="stylesheet" TYPE="text/css" HREF="res:/ui/css/tutorial.css">\n                </head>\n                <body>'
            tutData = None
            if VID:
                tutData = sm.RemoteSvc('tutorialSvc').GetTutorialInfo(VID)
            elif tutorialID:
                tutData = self.GetTutorialInfo(tutorialID)
            if tutData:
                if tutorialBrowser and tutorialBrowser.destroyed:
                    return 
                goingBack = pageNo == -1
                pageCount = len(tutData.pages)
                if pageNo == -1:
                    pageNo = pageCount
                else:
                    pageNo = pageNo or 1
                if pageNo > pageCount:
                    log.LogWarn('Open Tutorial Page Failed:, have page %s but max %s pages. falling back to page 1 :: tutorialID: %s, sequenceID: %s, VID: %s' % (pageNo,
                     pageCount,
                     tutorialID,
                     sequenceID,
                     VID))
                    pageNo = 1
                (dispPageNo, dispPageCount,) = (pageNo, pageCount)
                pageData = tutData.pages[(pageNo - 1)]
                caption = tutorialBrowser.sr.captionText
                caption.fontsize = 18
                caption.linespace = 16
                caption.letterspace = 2
                loop = 1
                while 1:
                    caption.text = localization.GetByMessageID(tutData.tutorial[0].tutorialNameID)
                    if pageData and pageData.pageName:
                        tutorialBrowser.sr.subcaption.text = localization.GetByMessageID(pageData.pageNameID)
                        tutorialBrowser.sr.subcaption.state = uiconst.UI_DISABLED
                    else:
                        tutorialBrowser.sr.subcaption.state = uiconst.UI_HIDDEN
                    if caption.textheight < 52 or not loop:
                        break
                    caption.fontsize = 13
                    caption.letterspace = 0
                    caption.linespace = 12
                    caption.last = (0, 0)
                    loop = 0

                if sequenceID:
                    check = []
                    seqTutData = self.GetTutorialInfo(tutorialID)
                    for criteria in seqTutData.criterias:
                        cd = self.GetCriteria(criteria.criteriaID)
                        if cd is None:
                            continue
                        check.append(criteria)

                    closeToEnd = 0
                    for criteria in seqTutData.pagecriterias:
                        if criteria.pageID == pageData.pageID:
                            check.append(criteria)
                            closeToEnd = 1
                        elif not closeToEnd:
                            cd = self.GetCriteria(criteria.criteriaID)
                            if cd is None:
                                continue
                            if not cd.criteriaName.startswith('rookieState'):
                                continue
                            check.append(criteria)

                    actionData = seqTutData.actions
                    pageActionData = seqTutData.pageactions
                else:
                    check = [ c for c in tutData.criterias ]
                    for criteria in tutData.pagecriterias:
                        if criteria.pageID == pageData.pageID:
                            check.append(criteria)

                    actionData = tutData.actions
                    pageActionData = tutData.pageactions
                actions = [ self.GetAction(action.actionID) for action in actionData ]
                actions += [ self.GetAction(action.actionID) for action in pageActionData if action.pageID == pageData.pageID ]
                preRookieState = eve.rookieState
                if skipCriteria:
                    criteriaCheck = None
                else:
                    criteriaCheck = self.ParseCriterias(check, 'tut', tutorialBrowser, tutorialID)
                if not tutorialBrowser or getattr(tutorialBrowser, 'sr', None) is None:
                    return 
                if criteriaCheck:
                    if preRookieState:
                        eve.SetRookieState(preRookieState)
                    body += '<br>' + localization.GetByMessageID(criteriaCheck.messageTextID)
                    if pageNo > 1 or sequenceID and self.GetNextInSequence(tutorialID, sequenceID, -1):
                        tutorialBrowser.sr.back.state = uiconst.UI_NORMAL
                    if self.waitingForWarpConfirm == False:
                        tutorialBrowser.sr.next.state = uiconst.UI_NORMAL
                        tutorialBrowser.sr.next.OnClick = self.Reload
                        tutorialBrowser.Confirm = self.Reload
                        tutorialBrowser.sr.next.SetLabel(localization.GetByLabel('UI/Commands/Next'))
                        tutorialBrowser.sr.text.text = ''
                    tutorialBrowser.sr.back.OnClick = self.Back
                    if checkBack:
                        tutorialBrowser.reverseBack = 1
                else:
                    self.ParseActions(actions)
                    tutorialBrowser.sr.text.text = localization.GetByLabel('UI/Tutorial/PageOf', num=dispPageNo, total=dispPageCount)
                    if pageNo > 1 or sequenceID and self.GetNextInSequence(tutorialID, sequenceID, -1):
                        tutorialBrowser.sr.back.state = uiconst.UI_NORMAL
                    self.SetCriterias(check)
                    if pageData:
                        page = pageData
                        body += '%s' % localization.GetByMessageID(page.textID)
                        tutorialBrowser.sr.next.state = uiconst.UI_NORMAL
                        tutorialBrowser.sr.next.OnClick = self.Next
                        tutorialBrowser.Confirm = self.Next
                        tutorialBrowser.sr.back.OnClick = self.Back
                        if pageNo < pageCount or sequenceID and self.GetNextInSequence(tutorialID, sequenceID):
                            tutorialBrowser.sr.next.SetLabel(localization.GetByLabel('UI/Commands/Next'))
                        else:
                            tutorialBrowser.sr.next.SetLabel(localization.GetByLabel('UI/Commands/Done'))
                            tutorialBrowser.done = 1
                        imagePath = page.imagePath
                body += '\n                            Page %s was not found in this tutorial.\n                            ' % pageNo
            else:
                tutorialBrowser.sr.captionText.text = localization.GetByLabel('UI/Tutorial/EveTutorials')
                body = '%s %s' % (localization.GetByLabel('UI/Tutorial/UnknownTutorial'), tutorialID)
            body += '</body></html>'
            self.CheckTopHeight()
            tutorialBrowser.LoadHTML('', hideBackground=1, newThread=0)
            if tutorialBrowser.state == uiconst.UI_HIDDEN:
                tutorialBrowser.Maximize()
            if imagePath:
                self.LoadImage(imagePath)
            elif tutorialBrowser.sr.imgpar.state != uiconst.UI_HIDDEN:
                tutorialBrowser.sr.imgpar.state = uiconst.UI_HIDDEN
                uiutil.Update()
            blue.pyos.synchro.Yield()
            goodies = sm.RemoteSvc('tutorialLocationSvc').GetTutorialGoodies(tutorialID, pageID, pageNo)
            goodieHtml = self.LoadAndGiveGoodies(goodies, tutorialID, pageID, pageNo)
            if goodieHtml:
                body += '<br>%s' % goodieHtml
            tutorialBrowser.LoadHTML(body, hideBackground=1, newThread=0)
            tutorialBrowser.SetCaption(localization.GetByLabel('UI/Tutorial/UnknownTutorial'))
            if not hasattr(tutorialBrowser, 'current') or tutorialBrowser.current[4] != sequenceID:
                tutorialBrowser.startTime = blue.os.GetWallclockTime()
            tutorialBrowser.current = (tutorialID,
             pageNo,
             pageID,
             pageCount,
             sequenceID,
             VID,
             pageData.pageActionID)
            if sequenceID:
                if tutorialBrowser.done:
                    self.SetSequenceStatus(sequenceID, tutorialID, pageNo, 'done')
                else:
                    self.SetSequenceStatus(sequenceID, tutorialID, pageNo)
                if not self.CheckTutorialDone(sequenceID, tutorialID):
                    self.SetSequenceDoneStatus(sequenceID, tutorialID, pageNo)
            found = False
            for page in tutData.pages:
                if page.pageID == pageID or page.pageNumber == pageNo:
                    if not criteriaCheck:
                        translatedText = localization.GetByMessageID(page.uiPointerTextID)
                        self.uiPointerSvc.PointTo(page.uiPointerID, translatedText)
                        found = True
                        break

            if found == False:
                self.uiPointerSvc.ClearPointers()

        finally:
            self.loadingTutorial = 0




    def CheckTopHeight(self):
        tutorialBrowser = self.GetTutorialBrowser()
        if not tutorialBrowser:
            return 
        h = 0
        for each in tutorialBrowser.sr.tTop.children:
            if each.state != uiconst.UI_HIDDEN:
                h += each.height + each.top

        tutorialBrowser.SetTopparentHeight(max(64, h))



    def FindInChildren(self, container, subContainerName):
        if container is None:
            return 
        if hasattr(container, 'children'):
            for child in container.children:
                if child.name == subContainerName:
                    return child




    def LoadAndGiveGoodies(self, goodies, tutorialID, pageID, pageNo):
        goodieHtml = ''
        if len(goodies) != 0:
            if goodies[0] == -1:
                goodieHtml += '\n                        <br>\n                        <font size=12>%s</font>\n                        <br><br>\n                ' % localization.GetByLabel('UI/Tutorial/TutorialGoodie/AlreadyReceived')
                return goodieHtml
            for goodie in goodies:
                type = cfg.invtypes.Get(goodie.invTypeID)
                goodieHtml += '\n                        <hr>\n                        <p>\n                        <img style=margin-right:0;margin-bottom:0 src="typeicon:typeID=%s&bumped=1&showFitting=0" align=left>\n                        <font size=20 margin-left=20>%s</font>\n                        <a href=showinfo:%s><img style:vertical-align:bottom src="icon:38_208" size=16 alt="%s"></a>\n                        <br>\n                        <font size=12>%s</font>\n                        <br>\n                        </p>\n                    ' % (goodie.invTypeID,
                 type.typeName,
                 goodie.invTypeID,
                 localization.GetByLabel('UI/Commands/ShowInfo'),
                 type.description)

            self.GiveGoodies(tutorialID, pageID, pageNo)
            return goodieHtml



    def GetGoodieInfo(self, *args):
        if len(args) > 0 and hasattr(args[0], 'typeID'):
            iconContainer = args[0]
            sm.StartService('info').ShowInfo(iconContainer.typeID)



    def LoadImage(self, imagePath):
        if not blue.ResFile().Open(imagePath):
            log.LogError('Image not found in res:', imagePath)
            return 
        (texture, tWidth, tHeight, bw, bh,) = sm.GetService('photo').GetTextureFromURL(imagePath, sizeonly=1, dontcache=1)
        tutorialBrowser = self.GetTutorialBrowser()
        tutorialBrowser.sr.img.state = uiconst.UI_NORMAL
        tutorialBrowser.sr.img.SetTexturePath(imagePath)
        tutorialBrowser.sr.img.width = tWidth
        tutorialBrowser.sr.img.height = tHeight
        tutorialBrowser.sr.imgpar.width = min(128, tWidth) + tutorialBrowser.sr.img.left + 5
        if tutorialBrowser.sr.imgpar.state != uiconst.UI_DISABLED:
            tutorialBrowser.sr.imgpar.state = uiconst.UI_DISABLED
            uiutil.Update(tutorialBrowser)



    def ClickSequence(self, box, *args):
        if self.CheckTutorialDone(box.sequenceID, box.tutorialID) or eve.session.role & service.ROLE_GML:
            self.OpenTutorial(box.tutorialID, sequenceID=box.sequenceID)
        elif eve.Message('AskSkipPartOfTutorial', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            self.OpenTutorial(box.tutorialID, sequenceID=box.sequenceID)



    def CheckTutorialDone(self, sequenceID, tutorialID):
        doneTutorialID = self.GetSequenceDoneStatus(sequenceID)[0]
        if doneTutorialID is None:
            return False
        seq = self.GetSequence(sequenceID)
        for _tutorialID in seq:
            if _tutorialID == tutorialID:
                return True
            if _tutorialID == doneTutorialID:
                return False

        return False



    def CheckAccelerationGateActivation(self):
        if getattr(self, 'nogateactivate', None):
            split_criteria = self.nogateactivate.criteriaName.split('.')
            if len(split_criteria) > 1:
                key = split_criteria[1]
                if self.Precondition_Checknameinballpark(key):
                    info = localization.GetByMessageID(self.nogateactivate.messageTextID)
                    eve.Message('CustomInfo', {'info': info})
                    return False
        return True



    def CheckWarpDriveActivation(self, currentSequenceID = None, currentTutorialID = None):
        if getattr(self, 'nowarpactive', None):
            split_criteria = self.nowarpactive.criteriaName.split('.')
            if len(split_criteria) > 1:
                key = split_criteria[1]
                tutorial_split_criteria = key.split(':')
                if len(tutorial_split_criteria) > 1:
                    (sequenceID, tutorialID,) = tutorial_split_criteria
                    if currentSequenceID is None:
                        currentSequenceID = sequenceID
                    if currentTutorialID is None:
                        currentTutorialID = tutorialID
                    (sequenceID, tutorialID,) = (int(sequenceID), int(tutorialID))
                    if sequenceID == currentSequenceID and not self.CheckTutorialDone(sequenceID, tutorialID):
                        info = localization.GetByMessageID(self.nowarpactive.messageTextID)
                        eve.Message('CustomInfo', {'info': info})
                        return False
        return True



    def IsInInventory(self, inventory, key, id, pre = '', flags = None):
        if not inventory:
            return False
        key = key.lower()
        func = getattr(inventory, 'List%s' % pre, None)
        for rec in func():
            if key.startswith('category') and rec.categoryID == id or key.startswith('group') and rec.groupID == id or key.startswith('type') and rec.typeID == id:
                if not flags:
                    return True
                if rec.flagID in flags:
                    return True

        return False



    def SetCriterias(self, criterias):
        self.nogateactivate = None
        self.nowarpactive = None
        for criteriaData in self.PrioritizeCriterias(criterias):
            split_criteria = criteriaData.criteriaName.split('.')
            if len(split_criteria) > 1:
                (funcName, key,) = split_criteria
                if funcName.lower() == 'IfNameInBallparkThenNoGateActivation'.lower():
                    self.nogateactivate = criteriaData
                elif funcName.lower() == 'IfNotTutorialDoneThenNoWarp'.lower():
                    self.nowarpactive = criteriaData




    def ParseCriterias(self, criterias, what = '', tutorialBrowser = None, tutorialID = None):
        for criteriaData in self.PrioritizeCriterias(criterias):
            split_criteria = criteriaData.criteriaName.split('.')
            if len(split_criteria) > 1:
                (funcName, key,) = split_criteria
                if funcName in ('stationsvc', 'stationbtnblink') and self.Precondition_Wndopen('map'):
                    _func = getattr(self, 'Precondition_Wndclosed', None)
                    uthread.new(self.WaitForCriteria, 'map', _func, tutorialBrowser)
                    return self.GetCriteria(174)
                if funcName in 'IfNotTutorialDoneThenNoWarp':
                    if not session.stationid and bool(session.solarsystemid):
                        r = self._TutorialSvc__WarpToTutorial()
                        if r[0] in (0, 2):
                            if r[0] == 0:
                                tutorialBrowser.CloseByUser()
                            if r[1] is not None:
                                ret = eve.Message(r[1])
                func = getattr(self, 'Precondition_%s' % funcName.capitalize(), None)
                if func:
                    ok = func(key)
                    if not ok:
                        if funcName.lower() in ('wndopen', 'wndclosed', 'session', 'stationsvc', 'checklocktarget', 'checkballpark', 'checknotinballpark', 'checkcomplex', 'checkactivemodule', 'checkcargo', 'checknotincargo', 'checkhangar', 'checknotinship', 'checknotinhangar', 'checkincargoorhangar', 'checknameinballpark', 'checknamenotinballpark', 'checkhasskill', 'checkskilltraining', 'checktutorialagent', 'checkdronebay', 'checknotindronebay', 'entityspawnproximity', 'inspaceorentityspawnproximity'):
                            uthread.new(self.WaitForCriteria, key, func, tutorialBrowser)
                        if funcName == 'checkBallpark' and key == 'groupCloud' and not self.IsShipWarping():
                            self.ShowWarpToButton()
                        if criteriaData.messageTextID:
                            return criteriaData
                        raise RuntimeError('ParseCriterias: Missing Criteria message!!!<br>Criteraname: (%s)' % criteriaData.criteriaName)
                else:
                    log.LogError('Unknown precondition', funcName, 'Precondition_%s' % funcName.capitalize())




    def WaitForCriteria(self, key, func, tutorialBrowser):
        self.waiting = tutorialBrowser
        while self.waiting and not self.waiting.destroyed and not func(key):
            blue.pyos.synchro.SleepWallclock(250)

        if self.waiting and not self.waiting.destroyed:
            self.ReloadTutorialBrowser(self.waiting)



    def PrioritizeCriterias(self, criterias):
        criteriaData = [ self.GetCriteria(criteria.criteriaID) for criteria in criterias ]
        other = []
        rookieCheck = []
        for (i, cd,) in enumerate(criteriaData):
            if not cd:
                continue
            if cd.criteriaName.startswith('rookieState'):
                c = cd.criteriaName.split('.')[-1].replace('_', '.')
                if c != 'None':
                    rookieCheck.append((float(c), cd))
                else:
                    rookieCheck.append((0.0, cd))
            elif cd.criteriaName.startswith('IfNotTutorialDoneThenNoWarp') and cd not in other:
                other.append((0, cd))
            elif cd not in other:
                other.append((i, cd))

        rookieCheck = uiutil.SortListOfTuples(rookieCheck)
        other = uiutil.SortListOfTuples(other)
        return rookieCheck[-1:] + other



    def Precondition_Ifnameinballparkthennogateactivation(self, *args):
        return True



    def Precondition_Ifnottutorialdonethennowarp(self, *args):
        return True



    def Precondition_Rookiestate(self, key):
        if key == 'None':
            eve.SetRookieState(None)
        else:
            eve.SetRookieState(float(key.replace('_', '.')))
        return True



    def Precondition_Session(self, key):
        key = key.lower()
        if key == 'station':
            return bool(eve.session.stationid)
        if key == 'inflight':
            (sol, bp,) = (False, False)
            sol = bool(eve.session.solarsystemid)
            if sol:
                bp = bool(sm.GetService('michelle').GetRemotePark())
            return sol and bp
        if key in ('station_inflight', 'inflight_station'):
            return bool(eve.session.stationid) or bool(eve.session.solarsystemid)



    def Precondition_Checkballpark(self, key):
        if eve.session.solarsystemid:
            id = getattr(const, key, None)
            if not id:
                log.LogWarn('Precondition_Checkballpark Failed:, %s not found in const' % key)
                return False
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark is None:
                return False
            for (itemID, ball,) in ballpark.balls.iteritems():
                if ballpark is None:
                    break
                slimItem = ballpark.GetInvItem(itemID)
                if not slimItem:
                    continue
                if key.startswith('category') and slimItem.categoryID == id:
                    return True
                if key.startswith('group') and slimItem.groupID == id:
                    return True
                if key.startswith('type') and slimItem.typeID == id:
                    return True

        return False



    def Precondition_Checknotinballpark(self, key):
        return not self.Precondition_Checkballpark(key)



    def Precondition_Checktutorialagent(self, key):
        if eve.session.stationid:
            agents = sm.GetService('agents').GetAgentsByStationID()[eve.session.stationid]
            tutAgents = sm.GetService('agents').GetTutorialAgentIDs()
            for agent in agents:
                if agent.agentID in tutAgents:
                    return True

        return False



    def Precondition_Checknameinballpark(self, key):
        if eve.session.solarsystemid:
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark is None:
                return False
            for (itemID, ball,) in ballpark.balls.iteritems():
                if ballpark is None:
                    break
                slimItem = ballpark.GetInvItem(itemID)
                if not slimItem:
                    continue
                if uix.GetSlimItemName(slimItem).replace(' ', '').lower() == key.replace(' ', '').lower():
                    return True

        return False



    def Precondition_Checknamenotinballpark(self, key):
        return not self.Precondition_Checknameinballpark(key)



    def Precondition_Checkcomplex(self, key):
        if eve.session.solarsystemid:
            return True
        return False



    def Precondition_Wndopen(self, key):
        self.LogInfo('Precondition_Wndopen key:', key)
        key = key.lower()
        if key == 'map':
            return sm.GetService('viewState').IsViewActive('systemmap', 'starmap')
        if key == 'tacticaloverlay':
            return not not settings.user.overview.Get('viewTactical', 0)
        if key == 'ships':
            key = form.ShipHangar.default_windowID
        elif key == 'items':
            key = form.ItemHangar.default_windowID
        elif key == 'cargo':
            key = 'shipCargo_%s' % eve.session.shipid
        elif key == 'dronebay':
            key = 'drones_%s' % eve.session.shipid
        if bool(uicls.Window.IsOpen(key)):
            return True
        if eve.session.stationid and sm.GetService('station').GetSvc(key) is not None:
            return True
        return False



    def Precondition_Wndclosed(self, key):
        return not self.Precondition_Wndopen(key)



    def Precondition_Stationsvc(self, key):
        self.LogInfo('Precondition_Stationsvc key:', key)
        key = key.lower()
        if eve.session.stationid:
            while not form.Lobby.GetIfOpen():
                blue.pyos.synchro.SleepWallclock(1)

            if key == 'reprocessingplant':
                return sm.GetService('reprocessing').IsVisible()
            if key == 'fitting':
                wnd = form.FittingWindow.GetIfOpen()
                if wnd:
                    wnd.Maximize()
                    return wnd
            return not not sm.GetService('station').GetSvc(key)
        return False



    def Precondition_Expanded(self, key):
        if eve.session.solarsystemid2:
            return sm.GetService('tactical').IsExpanded(key)
        return False



    def Precondition_Checklocktarget(self, key):
        if eve.session.solarsystemid2:
            targets = sm.GetService('target').GetTargets()
            if key == '*':
                return not not targets
            if key == 'None':
                return not targets
            if not targets:
                return False
            groupID = getattr(const, 'group%s' % key, None)
            if not groupID:
                log.LogWarn('Precondition_Checklocktarget Failed; %s is not recognized as group')
                return False
            for targetID in targets:
                slimItem = uix.GetBallparkRecord(targetID)
                if not slimItem:
                    continue
                if slimItem.groupID == groupID:
                    return True

        return False



    def Precondition_Checkactivemodule(self, key):
        if eve.session.shipid:
            module = uicore.layer.shipui.GetModuleForFKey(key)
            if not module:
                return False
            return module.def_effect.isActive
        return False



    def Precondition_Checkship(self, key, condname = 'Precondition_Checkship'):
        if eve.session.shipid:
            id = getattr(const, key, None)
            if not id:
                log.LogWarn('%s Failed:, %s not found in const' % (condname, key))
                return False
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            key = key.lower()
            if key.startswith('category'):
                return ship.categoryID == id
            if key.startswith('group'):
                return ship.groupID == id
            if key.startswith('type'):
                return ship.typeID == id
        return False



    def Precondition_Checknotinship(self, key):
        return not self.Precondition_Checkship(key, 'Precondition_Checknotinship')



    def Precondition_Checkfitted(self, key, condname = 'Precondition_Checkfitted'):
        if eve.session.shipid:
            id = getattr(const, key, None)
            if not id:
                log.LogWarn('%s Failed: %s not found in const' % (condname, key))
                return False
            inventory = sm.GetService('invCache').GetInventoryFromId(eve.session.shipid)
            return self.IsInInventory(inventory, key, id, flags=uix.FittingFlags())
        return False



    def Precondition_Checknotfitted(self, key):
        return not self.Precondition_Checkfitted(key, 'Precondition_Checknotfitted')



    def Precondition_Checkhangar(self, key, condname = 'Precondition_Checkhangar'):
        if eve.session.stationid:
            id = getattr(const, key, None)
            if not id:
                log.LogWarn('%s Failed:, %s not found in const' % (condname, key))
                return False
            inventory = sm.GetService('invCache').GetInventory(const.containerHangar)
            return self.IsInInventory(inventory, key, id)
        return False



    def Precondition_Checknotinhangar(self, key):
        return not self.Precondition_Checkhangar(key, 'Precondition_Checknotinhangar')



    def Precondition_Checkcargo(self, key, condname = 'Precondition_Checkcargo'):
        if eve.session.shipid:
            id = getattr(const, key, None)
            if not id:
                log.LogWarn('%s Failed: %s not found in const' % (condname, key))
                return False
            inventory = sm.GetService('invCache').GetInventoryFromId(eve.session.shipid)
            return self.IsInInventory(inventory, key, id, 'Cargo')
        return False



    def Precondition_Checknotincargo(self, key):
        return not self.Precondition_Checkcargo(key, 'Precondition_Checknotincargo')



    def Precondition_Checkdronebay(self, key, condname = 'Precondition_Checkdronebay'):
        if eve.session.shipid:
            id = getattr(const, key, None)
            if not id:
                log.LogWarn('%s Failed: %s not found in const' % (condname, key))
                return False
            inventory = sm.GetService('invCache').GetInventoryFromId(eve.session.shipid)
            return self.IsInInventory(inventory, key, id, 'DroneBay')
        return False



    def Precondition_Checknotindronebay(self, key):
        return not self.Precondition_Checkdronebay(key, 'Precondition_Checknotindronebay')



    def Precondition_Checkincargoorhangar(self, key):
        return self.Precondition_Checkcargo(key, 'Precondition_Checkincargoorhangar') or self.Precondition_Checkhangar(key, 'Precondition_Checkincargoorhangar')



    def Precondition_Checkskilltraining(self, key):
        inTraining = sm.GetService('skills').SkillInTraining()
        if not inTraining:
            return False
        if key == '*':
            return True
        id = getattr(const, key, None)
        if not id:
            log.LogWarn('Precondition_Checkskilltraining Failed:, %s not found in const' % key)
            return False
        if inTraining.typeID == id:
            return True
        return False



    def Precondition_Checkhasskill(self, key):
        id = getattr(const, key, None)
        if not id:
            log.LogWarn('Precondition_Checkhasskill Failed:, %s not found in const' % key)
            return False
        return not not sm.GetService('skills').HasSkill(id)



    def Precondition_Stationbtnblink(self, key):
        if eve.session.stationid:
            while not form.Lobby.GetIfOpen():
                blue.pyos.synchro.SleepWallclock(1)

            sm.GetService('station').BlinkButton(key)
        return True



    def Precondition_Shipuibtnblink(self, key):
        if eve.session.solarsystemid and uicore.layer.shipui.isopen:
            uicore.layer.shipui.BlinkButton(key)
        return True



    def Precondition_Headerblink(self, key):
        if eve.session.solarsystemid2:
            sm.GetService('tactical').BlinkHeader(key)
        return True



    def Precondition_Activeitembtnblink(self, key):
        if eve.session.solarsystemid2:
            selecteditem = form.ActiveItem.GetIfOpen()
            if selecteditem:
                selecteditem.BlinkBtn(key)
        return True



    def Precondition_Neocombtnblink(self, key):
        if eve.session.solarsystemid2:
            sm.GetService('neocom').Blink(key, blinkcount=60, frequency=500)
        return True



    def Precondition_Mapbtnblink(self, key):
        if eve.session.solarsystemid2:
            sm.GetService('map').BlinkBtn(key)
        return True



    def Precondition_Tutorialbtnblink(self, key):
        key = key.lower()
        tutorialBrowser = self.GetTutorialBrowser()
        if not tutorialBrowser:
            return False
        blue.pyos.synchro.Yield()
        if key == 'ok' and tutorialBrowser.sr.next:
            tutorialBrowser.sr.next.Blink()
        elif key == 'back' and tutorialBrowser.sr.back:
            tutorialBrowser.sr.back.Blink()
        return True



    def Precondition_Tutorialdone(self, key):
        tutorialBrowser = self.GetTutorialBrowser()
        if not tutorialBrowser:
            return False
        tutorialBrowser.done = True
        return True



    def Precondition_Windowpos(self, key):
        key = key.replace('dw', str(uicore.desktop.width)).replace('dh', str(uicore.desktop.height))
        pos = key.split(',')
        if len(pos) != 2:
            return False
        tutorialBrowser = self.GetTutorialBrowser()
        if not tutorialBrowser:
            return False
        tutorialBrowser.left = eval(pos[0])
        tutorialBrowser.top = eval(pos[1])
        return True



    def Precondition_Agentdialogueopen(self, key):
        for window in uicore.registry.GetWindows():
            if isinstance(window, form.AgentDialogueWindow):
                return True

        return False



    def Precondition_Characterhasanyskillinjected(self, key):
        skillSvc = sm.GetService('skills')
        skillIDs = key.split(',')
        for skillID in skillIDs:
            skillIDNum = int(skillID)
            if skillSvc.HasSkill(skillIDNum) is not None:
                return True

        return False


    entitySpawnDict = {1: {const.typeAmarrCaptainsQuarters: 2594,
         const.typeCaldariCaptainsQuarters: 2596,
         const.typeGallenteCaptainsQuarters: 2597,
         const.typeMinmatarCaptainsQuarters: 4544}}

    def Precondition_Entityspawnproximity(self, key):
        if not session.worldspaceid:
            return False
        (spawnIDType, distance,) = key.split(':')
        spawnIDType = int(spawnIDType)
        distance = float(distance)
        worldspaceTypeID = sm.GetService('worldSpaceClient').GetWorldSpaceTypeIDFromWorldSpaceID(session.worldspaceid)
        spawnID = self.entitySpawnDict.get(spawnIDType, {}).get(worldspaceTypeID, None)
        if spawnID is None or spawnID not in cfg.entitySpawns:
            return False
        spawnRow = cfg.entitySpawns.Get(spawnID)
        spawnPosition = (spawnRow.spawnPointX, spawnRow.spawnPointY, spawnRow.spawnPointZ)
        playerEnt = sm.GetService('entityClient').GetPlayerEntity()
        playerPos = playerEnt.GetComponent('position').position
        return geo2.Vec3Distance(playerPos, spawnPosition) <= distance



    def Precondition_Inspaceorentityspawnproximity(self, key):
        if self.Precondition_Session('inflight'):
            return True
        if self.Precondition_Entityspawnproximity(key):
            return True
        return False



    def ParseActions(self, actions):
        for action in actions:
            actionName = const.actionTypes[action.actionTypeID]
            function = getattr(self, 'Action_%s' % actionName, None)
            if function is None:
                msg = 'Unable to match tutorial action with action function. '
                msg += 'actionID: %s, actionTypeID: %s, actionType: %s.' % (action.actionID, action.actionTypeID, actionName)
                log.LogError(msg)
                return 
            function(action.actionData)




    def _ActionWaitForCriteria(self, criteria, actionData, func):
        tasklet = uthread.new(self._ActionWaitForCriteriaTasklet, criteria, actionData, func)
        tasklet.context = 'tutorial::_ActionWaitForCriteria'



    def _ActionWaitForCriteriaTasklet(self, criteria, actionData, func):
        waiting = self.GetTutorialBrowser(create=False)
        while True:
            blue.pyos.synchro.SleepWallclock(250)
            if not waiting or waiting.destroyed or waiting is not self.GetTutorialBrowser(create=False):
                return 
            for (preconditionFunc, key,) in criteria:
                passed = preconditionFunc(key)
                if not passed:
                    break

            if passed:
                break

        func(actionData)



    def _ParseActionCriteria(self, actionData):
        (actionData, junk, criteriaText,) = actionData.lower().partition('criteria=')
        criteriaText = criteriaText.strip().lstrip('[').rstrip(']')
        criteria = []
        for string in criteriaText.split('),'):
            (criteriaFuncName, junk, key,) = string.partition('(')
            key = key.rstrip(')')
            criteriaFunc = getattr(self, 'Precondition_%s' % criteriaFuncName.capitalize(), None)
            if criteriaFunc:
                criteria.append((criteriaFunc, key))

        return (criteria, actionData)



    def Action_Open_MLS_Message(self, actionData):
        eve.Message(actionData)



    def Action_Neocom_Button_Blink(self, actionData):
        actionData = actionData.lower()
        splitData = actionData.split('.')
        if len(splitData) == 3:
            (key, blinkcount, frequency,) = splitData
            sm.GetService('neocom').Blink(key, blinkcount=int(blinkcount), frequency=int(frequency))
        else:
            sm.GetService('neocom').Blink(actionData)



    def Action_Play_MLS_Audio(self, actionData):
        message = cfg.GetMessage(actionData)
        audioName = message.audio
        if not audioName:
            return 
        if audioName.startswith('wise:/'):
            audioName = audioName[6:]
        self.audioEmitter.SendEvent(u'stop_all_sounds')
        self.audioEmitter.SendEvent(unicode(audioName))



    def Action_Poll_Criteria_Open_Tutorial(self, actionData):
        (criteria, actionData,) = self._ParseActionCriteria(actionData)
        self._ActionWaitForCriteria(criteria, actionData, self._Action_Open_Tutorial)



    def _Action_Open_Tutorial(self, actionData):
        actionData = actionData.lower().lstrip('tutorialid=')
        (tutorialID, junk, actionData,) = actionData.partition(',')
        pageNo = actionData.lstrip('pageno=').strip(',')
        tutorialID = int(tutorialID)
        pageNo = int(pageNo) if pageNo else None
        self.OpenTutorialSequence_Check(tutorialID=tutorialID, force=True, pageNo=pageNo)



    def GetCharacterTutorialState(self):
        self.tutorialNoob = blue.os.GetWallclockTime() < sm.RemoteSvc('userSvc').GetCreateDate() + 14 * const.DAY
        showTutorials = settings.char.ui.Get('showTutorials', None)
        sequenceStatus = settings.char.ui.Get('SequenceStatus', None)
        sequenceDoneStatus = settings.char.ui.Get('SequenceDoneStatus', None)
        if showTutorials is not None and sequenceStatus is not None and sequenceDoneStatus is not None:
            return 
        rs = sm.RemoteSvc('tutorialSvc').GetCharacterTutorialState()
        if not rs or len(rs) == 0:
            return 
        tutorials = self.GetTutorials()
        previousTutorialIdFromTutorialId = {}
        for tutorialID in tutorials.keys():
            tutorial = tutorials[tutorialID]
            nextTutorialID = self.GetNextTutorial(tutorialID)
            if not nextTutorialID:
                continue
            previousTutorialIdFromTutorialId[nextTutorialID] = tutorialID

        sequenceStatus = {}
        sequenceDoneStatus = {}
        for r in rs:
            showTutorials = int(r.eventTypeID != 158)
            if not showTutorials:
                continue
            sequence = []
            tutorialID = r.tutorialID
            i = 0
            while tutorialID not in self.GetValidTutorials():
                i += 1
                if i > 100:
                    break
                tutorialID = previousTutorialIdFromTutorialId.get(tutorialID, None)
                if tutorialID:
                    sequence.append(tutorialID)

            sequenceStatus[tutorialID] = [(r.tutorialID, r.pageID), 'done'][(r.eventTypeID in (155, 158))]
            sequenceDoneStatus[tutorialID] = (r.tutorialID, 1)

        if showTutorials is not None:
            settings.char.ui.Set('showTutorials', showTutorials)
        if len(sequenceStatus):
            settings.char.ui.Set('SequenceStatus', sequenceStatus)
        if len(sequenceDoneStatus):
            settings.char.ui.Set('SequenceDoneStatus', sequenceDoneStatus)



    def ChangeTutorialWndState(self, visible = 0):
        tutorialWnd = form.TutorialWindow.GetIfOpen()
        if tutorialWnd:
            state = settings.char.ui.Get('tutorialHiddenUIState', uiconst.UI_NORMAL)
            if visible:
                tutorialWnd.state = state
                settings.char.ui.Delete('tutorialHiddenUIState')
            elif state != uiconst.UI_HIDDEN:
                settings.char.ui.Set('tutorialHiddenUIState', tutorialWnd.state)
                tutorialWnd.state = uiconst.UI_HIDDEN



    def GetCareerFunnelAgents(self):
        if len(self.careerAgents):
            return self.careerAgents
        agentMapping = sm.RemoteSvc('tutorialSvc').GetCareerAgents()
        for careerType in agentMapping:
            agentIDs = []
            if careerType not in self.careerAgents:
                self.careerAgents[careerType] = {}
                self.careerAgents[careerType]['agent'] = {}
                self.careerAgents[careerType]['station'] = {}
            agentIDs = agentMapping.get(careerType, [])
            agents = sm.RemoteSvc('tutorialSvc').GetTutorialAgents(agentIDs)
            for agent in agents:
                self.careerAgents[careerType]['agent'][agent.agentID] = agent
                self.careerAgents[careerType]['station'][agent.agentID] = sm.RemoteSvc('stationSvc').GetStation(agent.stationID)


        return self.careerAgents




class TutorialWindow(form.VirtualBrowser):
    __guid__ = 'form.TutorialWindow'
    default_windowID = 'aura9'
    default_width = 350
    default_height = 240

    @staticmethod
    def default_top(*args):
        return uicore.desktop.height - 270



    @staticmethod
    def default_left(*args):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return uicore.desktop.width - 360 - rightpush



    def CloseByUser(self, *args):
        sm.GetService('tutorial').AskClose()




class CareerFunnelWindow(uicls.Window):
    __guid__ = 'form.CareerFunnelWindow'
    default_windowID = 'careerFunnel'
    notifiers = None

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.currWidth = 600
        self.inited = False
        self.contentItemList = []
        self.SetTopparentHeight(0)
        self.MakeUnResizeable()
        self.MakeUnstackable()
        self.width = self.currWidth
        self.left = 0
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        self.left += leftpush
        self.top = 0
        self.SetWndIcon('03_10', hidden=True)
        self.SetCaption(localization.GetByLabel('UI/Tutorial/CareerFunnel'))
        self.height = 500
        self.SetMinSize([self.currWidth, self.height])
        self.headerText = uicls.EveCaptionMedium(text=localization.GetByLabel('UI/Tutorial/CareerFunnelHeader'), parent=self.sr.main, align=uiconst.TOTOP, padding=const.defaultPadding * 2, state=uiconst.UI_DISABLED)
        self.textObject = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Tutorial/CareerFunnelIntro'), parent=self.sr.main, padLeft=const.defaultPadding * 2, padRight=const.defaultPadding * 2, padBottom=const.defaultPadding, state=uiconst.UI_DISABLED, align=uiconst.TOTOP)
        uicls.Line(align=uiconst.TOTOP, parent=self.sr.main)
        self.sr.contentList = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        noContentHint = localization.GetByLabel('UI/Generic/Unknown')
        if not len(self.contentItemList):
            careerAgents = self.GetAgents()
            agentNodes = None
            for career in careerAgents:
                agentToUse = None
                jumps = 999
                for agentID in careerAgents[career]['agent']:
                    agent = careerAgents[career]['agent'][agentID]
                    station = careerAgents[career]['station'][agentID]
                    jumpsToAgent = sm.GetService('pathfinder').GetJumpCountFromCurrent(station.solarSystemID)
                    if jumpsToAgent < jumps:
                        agentToUse = agentID
                        jumps = jumpsToAgent

                if agentToUse:
                    data = {'agent': careerAgents[career]['agent'][agentToUse],
                     'career': career,
                     'agentStation': careerAgents[career]['station'][agentToUse]}
                    self.contentItemList.append(listentry.Get('CarrierAgentEntry', data))
                else:
                    noContentHint = localization.GetByLabel('UI/Generic/NoRouteCanBeFound')

        self.sr.contentList.Startup()
        self.sr.contentList.ShowHint()
        self.sr.contentList.Load(None, self.contentItemList, headers=None, noContentHint=noContentHint)
        height = self.headerText.textheight + self.headerText.padTop + self.headerText.padBottom
        height += self.textObject.textheight + self.textObject.padTop + self.textObject.padBottom
        height += 440
        self.height = height
        self.inited = True



    def GetAgents(self):
        return sm.GetService('tutorial').GetCareerFunnelAgents()



    def RefreshEntries(self):
        for content in self.contentItemList:
            if content.panel is not None:
                content.panel.Load(content)

        self.sr.contentList.Load(None, self.contentItemList, headers=None, noContentHint=localization.GetByLabel('UI/Generic/Unknown'))



    def CloseByUser(self, *args):
        if eve.Message('CareerFunnelClose', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            uicls.WindowCore.CloseByUser(self)




class CarrierAgentEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.CarrierAgentEntry'

    def Startup(self, *etc):
        self.photoSvc = sm.StartService('photo')
        self.sr.cellContainer = uicls.Container(name='CellContainer', parent=self, padding=(2, 2, 2, 2))
        uicls.Frame(parent=self.sr.cellContainer, color=(1, 1, 1, 0.25))
        self.sr.agentContainer = uicls.Container(parent=self.sr.cellContainer, align=uiconst.TORIGHT, state=uiconst.UI_NORMAL, width=330)
        self.sr.careerContainer = uicls.Container(parent=self.sr.cellContainer, align=uiconst.TOALL, padding=(const.defaultPadding * 2,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))



    def Load(self, node):
        agent = node.agent
        agentID = agent.agentID
        career = node.career
        agentStation = node.agentStation
        agentStationID = agentStation.stationID
        agentSystemID = agentStation.solarSystemID
        agentConstellationID = sm.GetService('map').GetConstellationForSolarSystem(agentSystemID)
        agentRegionID = sm.GetService('map').GetRegionForSolarSystem(agentSystemID)
        agentNameText = cfg.eveowners.Get(agentID).name
        uiutil.Flush(self.sr.agentContainer)
        agentSprite = uicls.Sprite(name='AgentSprite', parent=self.sr.agentContainer, align=uiconst.RELATIVE, width=128, height=128, state=uiconst.UI_NORMAL, top=6)
        agentTextContainer = uicls.Container(name='TextContainer', parent=self.sr.agentContainer, align=uiconst.TOPLEFT, width=190, height=77, left=140)
        uicls.EveLabelLarge(text=agentNameText, parent=agentTextContainer, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padTop=const.defaultPadding)
        self.photoSvc.GetPortrait(agentID, 128, agentSprite)
        menuContainer = agentSprite
        menuContainer.GetMenu = lambda *args: self.GetAgentMenu(agent, agentStation)
        menuContainer.id = agentID
        menuContainer.OnClick = self.TalkToAgent
        menuContainer.cursor = uiconst.UICURSOR_SELECT
        agentButton = uicls.Button(parent=self.sr.agentContainer, align=uiconst.BOTTOMRIGHT, label=localization.GetByLabel('UI/Generic/Unknown'), fixedwidth=196, left=const.defaultPadding, top=const.defaultPadding)
        agentButton.func = self.SetDestination
        agentButton.args = (agentStationID,)
        agentButton.SetLabel(localization.GetByLabel('UI/Commands/SetDestination'))
        agentButton.state = uiconst.UI_NORMAL
        if session.stationid is None and agentSystemID == session.solarsystemid:
            hint = menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameSystem')
            agentButton.func = self.DockAtStation
            agentButton.args = (agentStationID,)
            agentButton.SetLabel(localization.GetByLabel('UI/Tutorial/WarpToAgentStation'))
        elif session.stationid == agentStationID:
            hint = menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameStation')
            agentButton.func = self.TalkToAgent
            agentButton.args = (agentID,)
            agentButton.SetLabel(localization.GetByLabel('UI/Commands/StartConversation'))
        elif session.stationid is not None:
            hint = menuContainer.hint = localization.GetByLabel('UI/Tutorial/YouNeedToExitTheStation')
        else:
            hint = localization.GetByLabel('UI/Tutorial/ThisStationIsInADifferentSolarSystem', setDestination=localization.GetByLabel('UI/Commands/SetDestination'))
            if session.constellationid == agentConstellationID:
                menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameConstellation')
            elif session.regionid == agentRegionID:
                menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameRegion')
            else:
                menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentNotInSameRegion')
        linktext = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (agentStation.stationTypeID,
         agentStationID,
         hint,
         agentStation.stationName)
        linkObject = uicls.EveLabelMedium(text=linktext, parent=agentTextContainer, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, padTop=const.defaultPadding, lineSpacing=-0.2)
        uiutil.Flush(self.sr.careerContainer)
        careerText = localization.GetByLabel('UI/Generic/Unknown')
        careerDesc = localization.GetByLabel('UI/Generic/Unknown')
        if career == 'industry':
            careerText = localization.GetByLabel('UI/Tutorial/Industry')
            careerDesc = localization.GetByLabel('UI/Tutorial/IndustryDesc')
        elif career == 'business':
            careerText = localization.GetByLabel('UI/Tutorial/Business')
            careerDesc = localization.GetByLabel('UI/Tutorial/BusinessDesc')
        elif career == 'military':
            careerText = localization.GetByLabel('UI/Tutorial/Military')
            careerDesc = localization.GetByLabel('UI/Tutorial/MilitaryDesc')
        elif career == 'exploration':
            careerText = localization.GetByLabel('UI/Tutorial/Exploration')
            careerDesc = localization.GetByLabel('UI/Tutorial/ExplorationDesc')
        elif career == 'advMilitary':
            careerText = localization.GetByLabel('UI/Tutorial/AdvMilitary')
            careerDesc = localization.GetByLabel('UI/Tutorial/AdvMilitaryDesc')
        titleContainer = uicls.Container(name='TitleContainer', parent=self.sr.careerContainer, align=uiconst.TOTOP, height=24)
        uicls.EveCaptionMedium(text=careerText, parent=titleContainer, state=uiconst.UI_DISABLED)
        uicls.EveLabelMedium(text=careerDesc, parent=self.sr.careerContainer, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, lineSpacing=-0.2)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 142
        return node.height



    def DockAtStation(self, *args):
        if len(args) > 0:
            stationID = args[0]
            sm.StartService('menu').Dock(stationID)



    def GetAgentMenu(self, agent, station):
        m = sm.StartService('menu').CharacterMenu(agent.agentID)
        char = cfg.eveowners.Get(agent.agentID)
        m += [(localization.GetByLabel('UI/Commands/ShowInfo'), sm.StartService('menu').ShowInfo, (int(char.Type()),
           agent.agentID,
           0,
           None,
           None))]
        if station.solarSystemID == session.solarsystemid:
            m += [None]
            m += [(localization.GetByLabel('UI/Tutorial/WarpToAgentStation'), self.DockAtStation, (station[0],))]
        return m



    def TalkToAgent(self, *args):
        if len(args) > 0:
            if hasattr(args[0], 'id'):
                agentID = args[0].id
            else:
                agentID = args[0]
            sm.StartService('agents').InteractWith(agentID)



    def SetDestination(self, stationID):
        if stationID is not None:
            sm.StartService('starmap').SetWaypoint(stationID, clearOtherWaypoints=True)




class GoodieInfoHelper():

    def __init__(self, itemID):
        self.itemID = itemID



    def GetMenu(self, *args):
        return [(localization.GetByLabel('UI/Commands/ShowInfo'), sm.StartService('info').ShowInfo, (self.itemID,))]




