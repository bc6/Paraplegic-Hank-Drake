import blue
import bluepy
import const
import copy
import log
import service
import uthread
import util
import cqscreen
import uiutil
import random
import corebrowserutil
import uix
import uicls
import uiconst
import urllib2
import os

class HoloscreenSvc(service.Service):
    __guid__ = 'svc.holoscreen'
    __displayname__ = 'Holoscreen service'
    RSS_FEEDS = ['http://www.eveonline.com/feed/rdfnews.asp?tid=7', 'http://www.eveonline.com/feed/rdfnews.asp?tid=4']
    __notifyevents__ = ['OnSessionChanged']

    def Run(self, memStream = None):
        self.mainScreen = None
        self.corpFinderScreen = None
        self.piScreen = None
        self.playlist = []
        self.currTemplate = 0
        self.mainScreenDesktop = None
        self.corpFinderScreenDesktop = None
        self.piScreenDesktop = None
        self.playThread = None
        self.holoscreenMgr = sm.RemoteSvc('holoscreenMgr')



    def Restart(self):
        self.SetDefaultPlaylist()
        if self.mainScreenDesktop:
            self.mainScreenDesktop.Flush()
        if self.mainScreen:
            self.mainScreen.Close()
            self.mainScreen = cqscreen.MainScreen(parent=self.mainScreenDesktop)
        if self.playThread:
            self.StopTemplates()
            self.PlayTemplates()



    def OnEntitySceneUnloaded(self, sceneID):
        if self.playThread:
            self.playThread.kill()
        self.mainScreen = None
        self.corpFinderScreen = None
        self.piScreen = None
        self.mainScreenDesktop = None
        self.corpFinderScreenDesktop = None
        self.piScreenDesktop = None



    def OnMainScreenDesktopCreated(self, desktop, entityID):
        self.mainScreenDesktop = desktop
        if prefs.GetValue('cqScreensEnabled', True):
            self.mainScreen = cqscreen.MainScreen(parent=desktop, entityID=entityID)
            self.PlayTemplates()
        else:
            self.mainScreen = uicls.Sprite(name='screenCenterFallback', parent=desktop, texturePath='res:/UI/Texture/classes/CQLoadingScreen/loadingScreen.png', align=uiconst.TOALL)
            self.mainScreen.entityID = entityID



    def ReloadMainScreen(self):
        self.StopTemplates()
        entityID = self.mainScreen.entityID
        self.mainScreen.Close()
        self.OnMainScreenDesktopCreated(self.mainScreenDesktop, entityID=entityID)



    def OnCorpFinderScreenDesktopCreated(self, desktop, entityID, newCorpID = None):
        if newCorpID is None:
            newCorpID = session.corpid
        self.corpFinderScreenDesktop = desktop
        if prefs.GetValue('cqScreensEnabled', True):
            self.corpFinderScreen = cqscreen.CorpFinderScreen(parent=self.corpFinderScreenDesktop, corpID=newCorpID, entityID=entityID)
        else:
            self.corpFinderScreen = uicls.Sprite(name='screenLeftFallback', parent=desktop, texturePath='res:/UI/Texture/classes/CQSideScreens/corpRecruitmentScreenBG.png', align=uiconst.TOALL)
            self.corpFinderScreen.entityID = entityID



    def OnSessionChanged(self, isremote, sess, change):
        if 'corpid' in change and change['corpid'][1]:
            if self.corpFinderScreen is not None:
                self.corpFinderScreen.ConstructCorpLogo(change['corpid'][1])



    def ReloadCorpFinderScreen(self, newCorpID = None):
        entityID = self.corpFinderScreen.entityID
        try:
            self.corpFinderScreen.Close()

        finally:
            self.OnCorpFinderScreenDesktopCreated(self.corpFinderScreenDesktop, entityID, newCorpID)




    def OnPIScreenDesktopCreated(self, desktop, entityID):
        self.piScreenDesktop = desktop
        if prefs.GetValue('cqScreensEnabled', True):
            self.piScreen = cqscreen.PIScreen(parent=desktop, entityID=entityID)
        else:
            self.piScreen = uicls.Sprite(name='screenRightFallback', parent=desktop, texturePath='res:/UI/Texture/classes/CQSideScreens/PIScreenBG.png', align=uiconst.TOALL)
            self.piScreen.entityID = entityID



    def ReloadPIScreen(self):
        entityID = self.piScreen.entityID
        try:
            self.piScreen.Close()

        finally:
            self.OnPIScreenDesktopCreated(self.piScreenDesktop, entityID)




    def PlayTemplates(self):
        self.SetDefaultPlaylist()
        self.playThread = uthread.new(self._PlayTemplates)
        self.mainScreen.SetNewsTickerData(*self.GetNewsTickerData())



    @bluepy.CCP_STATS_ZONE_METHOD
    def _PlayTemplates(self):
        while not self.mainScreen.destroyed:
            (template, data,) = self.GetNextTemplate()
            self.mainScreen.PlayTemplate(template, data)
            self.currTemplate += 1
            blue.pyos.synchro.Yield()




    def StopTemplates(self):
        if self.playThread:
            self.playThread.kill()
        self.currTemplate = 0



    def GetNextTemplate(self):
        if self.currTemplate >= len(self.playlist):
            self.currTemplate = 0
        (template, dataSource,) = self.playlist[self.currTemplate]
        try:
            if callable(dataSource):
                returnData = dataSource()
            else:
                returnData = dataSource
        except:
            log.LogException()
            returnData = None
        return (template, returnData)



    def SetTemplates(self, templateList):
        self.playlist = templateList



    def SetDefaultPlaylist(self):
        self.playlist = [(cqscreen.templates.SOV, self.GetSOVTemplateData),
         (cqscreen.templates.CareerAgent, self.GetCareerAgentTemplateData),
         (cqscreen.templates.Incursion, self.GetIncursionTemplateData),
         (cqscreen.templates.ShipExposure, self.GetShipExposureTemplateData),
         (cqscreen.templates.RacialEpicArc, self.GetRacialEpicArcTemplateData),
         (cqscreen.templates.CharacterInfo, self.GetNPEEpicArcTemplateData),
         (cqscreen.templates.CharacterInfo, self.GetWantedTemplateData),
         (cqscreen.templates.Plex, self.GetPlexTemplateData),
         (cqscreen.templates.AuraMessage, self.GetSkillTrainingTemplateData),
         (cqscreen.templates.AuraMessage, self.GetCloneStatusTemplateData),
         (cqscreen.templates.VirtualGoodsStore, self.GetVirtualGoodsStoreTemplateData)]
        customVideos = self.GetCustomVideoPlaylist()
        if customVideos:
            self.playlist = customVideos + self.playlist



    def GetCustomVideoPlaylist(self):
        path = blue.os.cachepath + 'CQScreenVideos'
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except:
                pass
            return None
        playlist = []
        for fileName in os.listdir(path):
            if fileName.endswith('.bik'):
                videoPath = str(path + '/' + fileName)
                data = util.KeyVal(videoPath=videoPath)
                playlist.append((cqscreen.templates.FullscreenVideo, data))

        return playlist



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetSOVTemplateData(self):
        sovList = self.holoscreenMgr.GetTwoHourCache().sovChangesReport
        if sovList is not None and len(sovList) > 0:
            data = copy.deepcopy(random.choice(sovList))
            regionID = sm.GetService('map').GetRegionForSolarSystem(data.solarSystemID)
            solarSystemName = cfg.evelocations.Get(data.solarSystemID).name
            regionName = cfg.evelocations.Get(regionID).name
            oldOwnerName = cfg.eveowners.Get(data.oldOwnerID).ownerName
            newOwnerName = cfg.eveowners.Get(data.newOwnerID).ownerName
            textParams = {}
            textParams['solarSystemName'] = '<color=WHITE>%s</color>' % solarSystemName
            textParams['allianceName'] = newOwnerName
            data.middleText = mls.UI_HOLOSCREEN_SOVEREIGNTYMIDDLE % textParams
            textParams = {}
            textParams['solarSystemName'] = solarSystemName
            textParams['regionName'] = regionName
            textParams['oldAllianceName'] = oldOwnerName
            textParams['newAllianceName'] = newOwnerName
            data.bottomText = mls.UI_HOLOSCREEN_SOVEREIGNTYBOTTOM % textParams
            data.clickFunc = uicore.cmd.OpenSovDashboard
            data.clickFuncLabel = mls.UI_HOLOSCREEN_SOV_LABEL
            data.clickArgs = (data.solarSystemID,)
            return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetCareerAgentTemplateData(self):
        careerAgents = self.holoscreenMgr.GetRuntimeCache().careerAgents
        chosenCareerType = random.choice(careerAgents.keys())
        if chosenCareerType == const.agentCareerTypeIndustry:
            careerText = mls.UI_TUTORIAL_INDUSTRY
            careerDesc = mls.UI_TUTORIAL_INDUSTRY_DESC
        elif chosenCareerType == const.agentCareerTypeBusiness:
            careerText = mls.UI_TUTORIAL_BUSINESS
            careerDesc = mls.UI_TUTORIAL_BUSINESS_DESC
        elif chosenCareerType == const.agentCareerTypeMilitary:
            careerText = mls.UI_TUTORIAL_MILITARY
            careerDesc = mls.UI_TUTORIAL_MILITARY_DESC
        elif chosenCareerType == const.agentCareerTypeExploration:
            careerText = mls.UI_TUTORIAL_EXPLORATION
            careerDesc = mls.UI_TUTORIAL_EXPLORATION_DESC
        elif chosenCareerType == const.agentCareerTypeAdvMilitary:
            careerText = mls.UI_TUTORIAL_ADVMILITARY
            careerDesc = mls.UI_TUTORIAL_ADVMILITARY_DESC
        agentStationDict = {}
        for row in careerAgents[chosenCareerType]:
            agentStationDict[row.agentID] = row

        nearAgentList = []
        nearestDist = 9999999
        for row in careerAgents[chosenCareerType]:
            dist = sm.GetService('pathfinder').GetJumpCountFromCurrent(row.solarSystemID)
            if dist < nearestDist:
                nearAgentList = []
                nearestDist = dist
            if dist == nearestDist:
                nearAgentList.append((row.agentID, row.stationID))

        if not nearAgentList:
            return None
        (chosenAgentID, chosenStationID,) = random.choice(nearAgentList)
        careerAdData = util.KeyVal()
        careerAdData.agentID = chosenAgentID
        careerAdData.stationID = chosenStationID
        careerAdData.jumpDistance = nearestDist
        stationName = cfg.evelocations.Get(careerAdData.stationID).locationName
        careerVideoPath = {const.agentCareerTypeIndustry: 'res:/video/cq/CQ_TEMPLATE_CAREER_INDUSTRY.bik',
         const.agentCareerTypeBusiness: 'res:/video/cq/CQ_TEMPLATE_CAREER_TRADE_BUSINESS.bik',
         const.agentCareerTypeMilitary: 'res:/video/cq/CQ_TEMPLATE_CAREER_MILITARY.bik',
         const.agentCareerTypeExploration: 'res:/video/cq/CQ_TEMPLATE_CAREER_EXPLORATION.bik',
         const.agentCareerTypeAdvMilitary: 'res:/video/cq/CQ_TEMPLATE_CAREER_ADVANCED_MILITARY.bik'}.get(chosenCareerType)
        data = util.KeyVal()
        data.charID = chosenAgentID
        data.headingText = '<fontsize=60>' + careerText
        data.subHeadingText = mls.UI_HOLOSCREEN_CAREERAGENTS_TITLE
        data.mainText = '<fontsize=20>' + careerDesc + '\n\n' + mls.UI_HOLOSCREEN_CAREERAGENT_INFO % {'stationName': stationName}
        data.clickFunc = sm.StartService('tutorial').ShowCareerFunnel
        data.clickFuncLabel = mls.UI_HOLOSCREEN_CAREER_AGENT_LABEL
        data.introVideoPath = 'res:/video/cq/LOGO_CONCORD.bik'
        data.careerVideoPath = careerVideoPath
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetIncursionTemplateData(self):
        incursionList = self.holoscreenMgr.GetTwoHourCache().incursionReport
        if not incursionList:
            return 
        chosenIncursion = random.choice(incursionList)
        solarSystemName = cfg.evelocations.Get(chosenIncursion.stagingSolarSystemID).name
        constellationID = sm.GetService('map').GetConstellationForSolarSystem(chosenIncursion.stagingSolarSystemID)
        constellationName = cfg.evelocations.Get(constellationID).name
        securityLevel = str(sm.GetService('map').GetSecurityStatus(chosenIncursion.stagingSolarSystemID))
        jumpDistance = sm.GetService('pathfinder').GetJumpCountFromCurrent(chosenIncursion.stagingSolarSystemID)
        jumpDistanceText = '(%s)' % (uix.Plural(jumpDistance, 'UI_SHARED_NUM_JUMP') % {'num': jumpDistance})
        data = util.KeyVal()
        data.headingText = mls.UI_HOLOSCREEN_INCURSION_HEADER
        data.introVideoPath = 'res:/video/cq/LOGO_CONCORD.bik'
        data.videoPath = 'res:/video/cq/CQ_TEMPLATE_INCURSION.bik'
        data.constellationText = '<color=orange>' + constellationName
        data.systemInfoText = '<color=red>' + securityLevel
        data.systemInfoText += ' <color=orange>' + solarSystemName
        data.systemInfoText += ' <color=white>' + jumpDistanceText
        data.influence = chosenIncursion.influence
        data.bottomText = mls.UI_HOLOSCREEN_INCURSION_NEWSFEED % {'constellationName': constellationName}
        data.clickFunc = sm.GetService('journal').ShowIncursionTab
        data.clickArgs = (None,
         None,
         None,
         True)
        data.clickFuncLabel = mls.UI_HOLOSCREEN_INCURSION_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetShipExposureTemplateData(self):
        if not eve.stationItem:
            return 
        racialShips = {const.raceAmarr: [2006,
                           20183,
                           24696,
                           24692,
                           597,
                           1944,
                           624],
         const.raceCaldari: [621,
                             20185,
                             24698,
                             640,
                             602,
                             648,
                             623],
         const.raceGallente: [627,
                              20187,
                              24700,
                              641,
                              593,
                              650,
                              626],
         const.raceMinmatar: [629,
                              20189,
                              24702,
                              644,
                              587,
                              653,
                              622]}
        oreShipsList = [17478, 17476, 2998]
        racialIntroVideos = {const.raceAmarr: 'res:/video/cq/LOGO_AMARR.bik',
         const.raceCaldari: 'res:/video/cq/LOGO_CALDARI.bik',
         const.raceGallente: 'res:/video/cq/LOGO_GALLENTE.bik',
         const.raceMinmatar: 'res:/video/cq/LOGO_MINMATAR.bik'}
        data = util.KeyVal()
        if random.random() <= 0.3:
            data.introVideoPath = 'res:/video/cq/LOGO_ORE.bik'
            data.shipTypeID = random.choice(oreShipsList)
        else:
            stationType = cfg.invtypes.Get(eve.stationItem.stationTypeID)
            stationRace = stationType['raceID']
            if stationRace not in racialShips:
                stationRace = const.raceGallente
            data.introVideoPath = racialIntroVideos[stationRace]
            data.shipTypeID = random.choice(racialShips[stationRace])
        shipCachedInfo = cfg.invtypes.Get(data.shipTypeID)
        data.shipName = shipCachedInfo.name
        data.shipGroupName = shipCachedInfo.Group().groupName
        data.buttonText = mls.UI_HOLOSCREEN_MARKET_AVAILABLE
        data.mainText = '<fontsize=30>' + mls.UI_HOLOSCREEN_SHIPDETAILS_TITLE
        data.mainText += '\n<fontsize=25>' + shipCachedInfo.description
        data.clickFunc = sm.GetService('marketutils').ShowMarketDetails
        data.clickArgs = (data.shipTypeID, None)
        data.clickFuncLabel = mls.UI_HOLOSCREEN_SHIP_EXPOSURE_LABEL % {'shipName': data.shipName}
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetRacialEpicArcTemplateData(self):
        epicArcList = self.holoscreenMgr.GetRuntimeCache().epicArcAgents
        if not epicArcList:
            return 
        if not eve.stationItem:
            return 
        epicArcData = random.choice(epicArcList)
        data = util.KeyVal()
        data.charID = epicArcData.agentID
        data.headingText = ''
        solarSystemID = sm.GetService('agents').GetSolarSystemOfAgent(epicArcData.agentID)
        regionID = sm.GetService('map').GetRegionForSolarSystem(solarSystemID)
        mainText = '<fontsize=30><color=WHITE>%(solarSystemString)s: %(solarSystemName)s\n%(regionString)s: %(regionName)s\n%(securityLevelString)s: %(securityLevel)s\n        '
        textParams = {}
        textParams['solarSystemString'] = mls.UI_GENERIC_SOLARSYSTEM
        textParams['solarSystemName'] = cfg.evelocations.Get(solarSystemID).locationName
        textParams['regionString'] = mls.UI_GENERIC_REGION
        textParams['regionName'] = cfg.evelocations.Get(regionID).locationName
        textParams['securityLevelString'] = mls.UI_GENERIC_SECURITY
        textParams['securityLevel'] = str(sm.GetService('map').GetSecurityStatus(solarSystemID))
        data.mainText = mainText % textParams
        epicArcDict = {48: (const.factionAmarrEmpire, mls.UI_HOLOSCREEN_EPICARCAMARR),
         52: (const.factionGallenteFederation, mls.UI_HOLOSCREEN_EPICARCGALLENTE),
         40: (const.factionCaldariState, mls.UI_HOLOSCREEN_EPICARCCALDARI),
         29: (const.factionSistersOfEVE, mls.UI_HOLOSCREEN_EPICARCSISTERS),
         53: (const.factionMinmatarRepublic, mls.UI_HOLOSCREEN_EPICARCMINMATAR),
         56: (const.factionAngelCartel, mls.UI_HOLOSCREEN_EPICARCANGELS),
         55: (const.factionGuristasPirates, mls.UI_HOLOSCREEN_EPICARCGURISTAS)}
        if epicArcData.epicArcID not in epicArcDict:
            return 
        (data.factionID, data.bottomText,) = epicArcDict.get(epicArcData.epicArcID, '')
        data.factionNameText = cfg.eveowners.Get(data.factionID).ownerName
        data.introVideoPath = {const.factionAmarrEmpire: 'res:/video/cq/LOGO_AMARR.bik',
         const.factionCaldariState: 'res:/video/cq/LOGO_CALDARI.bik',
         const.factionGallenteFederation: 'res:/video/cq/LOGO_GALLENTE.bik',
         const.factionMinmatarRepublic: 'res:/video/cq/LOGO_MINMATAR.bik',
         const.factionAngelCartel: 'res:/video/cq/LOGO_ANGELCARTEL.bik',
         const.factionGuristasPirates: 'res:/video/cq/LOGO_GURISTAS.bik',
         const.factionSistersOfEVE: 'res:/video/cq/LOGO_SISTERSOFEVE.bik'}.get(data.factionID, None)
        videoDict = {const.factionAmarrEmpire: 'res:/video/cq/CQ_TEMPLATE_EPICARC_AMARR.bik',
         const.factionCaldariState: 'res:/video/cq/CQ_TEMPLATE_EPICARC_CALDARI.bik',
         const.factionGallenteFederation: 'res:/video/cq/CQ_TEMPLATE_EPICARC_GALLENTE.bik',
         const.factionMinmatarRepublic: 'res:/video/cq/CQ_TEMPLATE_EPICARC_MINMATAR.bik',
         const.factionAngelCartel: 'res:/video/cq/CQ_TEMPLATE_EPICARC_MINMATAR.bik',
         const.factionGuristasPirates: 'res:/video/cq/CQ_TEMPLATE_EPICARC_CALDARI.bik'}
        factionKey = data.factionID
        if factionKey not in videoDict:
            stationItem = cfg.invtypes.Get(eve.stationItem.stationTypeID)
            factionKey = {const.raceAmarr: const.factionAmarrEmpire,
             const.raceCaldari: const.factionCaldariState,
             const.raceGallente: const.factionGallenteFederation,
             const.raceMinmatar: const.factionMinmatarRepublic}.get(stationItem['raceID'], const.factionGallenteFederation)
        data.videoPath = videoDict.get(factionKey, 'res:/video/cq/CQ_TEMPLATE_EPICARC_GALLENTE.bik')
        data.clickFunc = sm.GetService('agents').InteractWith
        data.clickArgs = (data.charID,)
        data.clickFuncLabel = mls.UI_HOLOSCREEN_RACIAL_EPIC_ARC_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetNewsAndLoreTemplateData(self):
        data = util.KeyVal()
        data.introVideoPath = 'res:/video/cq/CQ_NEWS_LORE_INTRO.bik'
        data.videoPath = 'res:/video/cq/CQ_TEMPLATE_SOVEREIGNTY.bik'
        data.clickFunc = uicore.cmd.OpenJournal
        data.clickFuncLabel = mls.UI_HOLOSCREEN_NEWS_AND_LORE_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetNPEEpicArcTemplateData(self):
        rookieList = self.holoscreenMgr.GetRecentEpicArcCompletions()
        if not rookieList:
            return None
        rookieData = random.choice(rookieList)
        data = util.KeyVal(charID=rookieData.characterID)
        charInfo = cfg.eveowners.Get(data.charID)
        completionDate = util.FmtDate(rookieData.completionDate)
        data.introVideoPath = 'res:/video/cq/LOGO_CONCORD.bik'
        data.heading = '<b>%s</b>' % uiutil.UpperCase(mls.UI_HOLOSCREEN_NPECOMPLETIONHEADING)
        data.mainText = '<fontsize=30>%s:\n' % mls.UI_HOLOSCREEN_NPECOMPLETIONCAPSULEERSTATUS
        data.mainText += '    %s\n' % charInfo.ownerName
        data.mainText += '%s:\n' % mls.UI_HOLOSCREEN_NPECOMPLETIONDATE
        data.mainText += '    %s\n\n' % completionDate
        data.mainText += '<fontsize=20>' + mls.UI_HOLOSCREEN_NPECOMPLETIONDISCLAIMER
        data.bottomText = mls.UI_HOLOSCREEN_NPECOMPLETIONBOTTOM % {'pilotName': charInfo.ownerName}
        data.isWanted = False
        data.clickFunc = sm.GetService('info').ShowInfo
        data.clickArgs = (charInfo.Type(), data.charID)
        data.clickFuncLabel = mls.UI_HOLOSCREEN_NPE_EPIC_ARC_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetWantedTemplateData(self):
        if not session.stationid or not eve.stationItem.serviceMask & const.stationServiceBountyMissions:
            return None
        topBounties = sm.RemoteSvc('charMgr').GetTopBounties()
        if not topBounties:
            return None
        chosenBounty = random.choice(topBounties)
        bountyName = chosenBounty.ownerName
        bountyAmount = util.FmtISK(chosenBounty.bounty)
        data = util.KeyVal()
        data.introVideoPath = 'res:/video/cq/LOGO_SCOPE.bik'
        data.charID = chosenBounty.characterID
        data.heading = '<b>%s</b>' % uiutil.UpperCase(mls.UI_HOLOSCREEN_WANTEDBOUNTYOFFER)
        data.mainText = '<fontsize=30>%s:\n' % mls.UI_HOLOSCREEN_WANTEDHEADING
        data.mainText += '<b><color=yellow><fontsize=50> %s\n</color></b>' % bountyName
        data.mainText += '<fontsize=30>%s:\n' % mls.UI_HOLOSCREEN_WANTEDBOUNTYOFFER
        data.mainText += '<b><fontsize=50> %s\n</b>' % bountyAmount
        data.mainText += '<fontsize=20>' + mls.UI_HOLOSCREEN_WANTEDDISCLAIMER
        data.bottomText = mls.UI_HOLOSCREEN_WANTEDNEWSFEED
        data.isWanted = True
        data.wantedHeading = mls.UI_HOLOSCREEN_WANTED_HEADER
        data.wantedText = mls.UI_HOLOSCREEN_WANTEDWARNING
        data.clickFunc = uicore.cmd.OpenMissions
        data.clickFuncLabel = mls.UI_HOLOSCREEN_WANTED_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetPlexTemplateData(self):
        data = util.KeyVal()
        data.introVideoPath = 'res:/video/cq/LOGO_CONCORD.bik'
        data.headingText = mls.UI_SHARED_PLEX_PURCHASE
        data.subHeadingText = mls.UI_SHARED_PILOTLICENSEEXTENSION
        data.buttonText = mls.UI_HOLOSCREEN_MARKET_AVAILABLE
        data.mainText = mls.UI_HOLOSCREEN_PLEX_MIDDLE
        data.clickFunc = sm.GetService('marketutils').ShowMarketDetails
        data.clickArgs = (const.typePilotLicence, None)
        data.clickFuncLabel = mls.UI_HOLOSCREEN_PLEX_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBillboardMessagesData(self):
        data = util.KeyVal()
        data.introVideoPath = 'res:/video/cq/LOGO_SCOPE.bik'
        data.videoPath = 'res:/video/cq/CQ_TEMPLATE_SOVEREIGNTY.bik'
        data.clickFunc = uicore.cmd.OpenCharactersheet
        data.clickFuncLabel = mls.UI_HOLOSCREEN_BILLBOARD_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetSkillTrainingTemplateData(self):
        if sm.GetService('skills').SkillInTraining() is not None:
            return 
        data = util.KeyVal()
        data.introVideoPath = 'res:/video/cq/LOGO_CONCORD.bik'
        data.headingText = uiutil.UpperCase(mls.UI_HOLOSCREEN_SKILLTRAININGTITLE)
        data.subHeadingText = mls.UI_HOLOSCREEN_SKILLTRAININGMIDDLE
        data.clickFunc = uicore.cmd.OpenSkillQueueWindow
        data.clickFuncLabel = mls.UI_HOLOSCREEN_SKILL_TRAINING_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetCloneStatusTemplateData(self):
        if not session.stationid or not eve.stationItem.serviceMask & const.stationServiceCloning:
            return None
        cloneTypeID = sm.GetService('charactersheet').GetCloneTypeID()
        if sm.GetService('godma').GetType(cloneTypeID).skillPointsSaved >= sm.GetService('skills').GetSkillPoints():
            return None
        data = util.KeyVal()
        data.introVideoPath = 'res:/video/cq/LOGO_CONCORD.bik'
        data.headingText = uiutil.UpperCase(mls.UI_HOLOSCREEN_CLONESTATUSTITLE)
        data.subHeadingText = mls.UI_HOLOSCREEN_CLONESTATUSMIDDLE
        data.clickFunc = uicore.cmd.OpenMedical
        data.clickFuncLabel = mls.UI_HOLOSCREEN_CLONE_LABEL
        return data



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetVirtualGoodsStoreTemplateData(self):
        data = util.KeyVal()
        data.introVideoPath = 'res:/video/cq/LOGO_QUAFE.bik'
        data.headingText = '<b>' + mls.UI_HOLOSCREEN_STOREGRANDOPENING
        data.clickFunc = uicore.cmd.OpenStore
        data.clickFuncLabel = mls.UI_CMD_OPENSTORE
        return data



    def GetNewsTickerData(self):
        newsData = []
        for url in self.RSS_FEEDS:
            try:
                rssData = corebrowserutil.GetStringFromURL(url)
            except urllib2.HTTPError:
                failData = util.KeyVal()
                failData.date = blue.os.GetTime()
                failData.link = 'http://www.eveonline.com'
                failData.title = 'The news service is temporarily unavailable.'
                newsData = [failData]
                clickFuncList = [ uicore.cmd.OpenBrowser for entry in newsData ]
                funcKeywordsList = [ {'url': entry.link} for entry in newsData ]
                return (newsData, clickFuncList, funcKeywordsList)
            except:
                log.LogException('Uncaught (non-http) error with the mainscreen news ticker in GetNewsTickerData()')
                failData = util.KeyVal()
                failData.date = blue.os.GetTime()
                failData.link = 'http://www.eveonline.com'
                failData.title = 'The news service is unavailable.'
                newsData = [failData]
                clickFuncList = [ uicore.cmd.OpenBrowser for entry in newsData ]
                funcKeywordsList = [ {'url': entry.link} for entry in newsData ]
                return (newsData, clickFuncList, funcKeywordsList)
            while True:
                line = rssData.readline()
                if not line:
                    break
                line = line.strip()
                if not line.startswith('<item rdf:about='):
                    continue
                entry = util.KeyVal()
                urlRaw = line.lstrip('<item rdf:about="').rstrip('">')
                entry.link = urlRaw.replace('&amp;', '&')
                while line != '</item>':
                    line = rssData.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line.startswith('<title>'):
                        entry.title = line.lstrip('<title>').rstrip('</title>')
                    elif line.startswith('<dc:date>'):
                        line = line.lstrip('<dc:date>').rstrip('</dc:date>')
                        (year, month, line,) = line.split('-')
                        (day, line,) = line.split('T')
                        (hour, line, temp,) = line.split(':')
                        (minute, line,) = line.split('+')
                        entry.date = blue.os.GetTimeFromParts(int(year), int(month), int(day), int(hour), int(minute), 0, 0)
                    elif line.startswith('<dc:extra'):
                        (temp, temp2, string,) = line.partition('mode="')
                        if string.startswith('solarsystem'):
                            (temp, temp2, string,) = string.partition('id="3">')
                            (string, temp, temp2,) = string.partition('</dc:extra')
                            entry.solarsystem = string
                        elif string.startswith('region'):
                            (temp, temp2, string,) = string.partition('id="5">')
                            (string, temp, temp2,) = string.partition('</dc:extra')
                            entry.region = string

                if not hasattr(entry, 'date'):
                    entry.date = 0
                newsData.append(entry)
                if not line:
                    break


        newsData.sort(key=lambda x: x.date, reverse=True)
        newsData = newsData[:15]
        clickFuncList = [ uicore.cmd.OpenBrowser for entry in newsData ]
        funcKeywordsList = [ {'url': entry.link} for entry in newsData ]
        return (newsData, clickFuncList, funcKeywordsList)




