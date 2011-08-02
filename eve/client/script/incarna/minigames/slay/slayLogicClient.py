import util
import math
import uiconst
import uthread
import cameras
import moniker
import slayConst
import minigames
import GameWorld
import slaycommon
import minigameConst
LIGHTS_OFF = {1: None,
 2: None,
 3: None,
 4: None,
 5: None,
 6: None}
SLAY_TABLE_HEIGHT = 1.3

class SlayLogicClient:
    __guid__ = 'minigames.SlayLogicClient'

    def __init__(self):
        self.lightsState = LIGHTS_OFF
        self.audioEmitter = None
        self.audio = None
        self.terminated = False
        self.entityID = None
        self.remoteController = None
        self.playing = False
        self.displayManager = None
        self.setupManager = None
        self.gameMasterSettings = None
        self.modelsManager = minigames.SlayModelManager(self)
        self.gameScore = None
        self.joined = False
        self.inUse = False
        self.currAvatarName = ''
        self.introDone = False
        self.exiting = False
        self.infoToDisplay = None
        self.selectedAreaID = None
        self.currPlayerID = None
        self.runningBet = None
        self.recordedGame = [[]]
        self.enemyActivities = util.KeyVal(moves=[], upgrades=[])
        self.areaEconomics = {}
        self.tableData = None
        self.compiledMap = slaycommon.SlayData()



    def Setup(self, entityID, model, config, state, audioEmitter):
        self.entityID = entityID
        self.placeableLocation = util.KeyVal(x=model.translation[0], y=model.translation[1], z=model.translation[2])
        self.modelsManager.Setup(model, config)
        self.gameConfiguration = config
        self.audioEmitter = audioEmitter
        self.audio = sm.GetService('audio')
        self.entityClient = sm.GetService('entityClient')
        self.gameui = sm.GetService('gameui')
        if state.get('gameData', False):
            self.lightsState = state['gameData'].lights
        if state.get('state', False) == minigameConst.GAME_STATE_WAITING_FOR_PEOPLE_TO_JOIN:
            self.modelsManager.StartFlashing()
        elif state.get('state', False) == minigameConst.GAME_STATE_GAME_IN_PROGRESS:
            self.tableData = state['gameData'].tiles
            self.modelsManager.Refresh(self.tableData)
        self.modelsManager.UpdateLights(self.lightsState)



    def BindRemoteController(self):
        if self.remoteController is None:
            self.remoteController = moniker.GetMinigameController(session.worldspaceid, self.entityID)



    def GameSetup(self, settings):
        self.gameMasterSettings = settings
        self.BindRemoteController()
        uthread.new(self.remoteController.GameSetup, self.entityID, settings)



    def SendMessageToServer(self, message, data):
        self.BindRemoteController()
        self.remoteController.Action(message, data)



    def JoinGame(self):
        if not self.gameConfiguration.open:
            eve.Message('CustomInfo', {'info': mls.UI_MINIGAME_TABLE_CLOSED})
            return 
        if not self.playing:
            self.BindRemoteController()
            uthread.new(self.remoteController.StartMinigame, self.entityID)



    def WalkTo(self, pos, rot):
        playerEntity = self.entityClient.GetPlayerEntity()
        playerEntity.movement.avatar.PushMoveMode(GameWorld.PathToMode(pos, 0.1, False, True))



    def ConfirmJoinGame(self, pickedColor):
        self.BindRemoteController()
        uthread.new(self.remoteController.ConfirmJoinGame, self.entityID, pickedColor)



    def Terminate(self):
        self.modelsManager.terminated = True
        self.ResetState()
        self.terminated = True



    def ProcessTriuiMessage(self, what_happened, *args):
        if hasattr(self.displayManager, 'running'):
            if what_happened == uiconst.UI_MOUSEDOWN:
                self.displayManager.OnMouseDownGlobal(*args)
            elif what_happened == uiconst.UI_MOUSEUP:
                self.displayManager.OnMouseUpGlobal(*args)
            elif what_happened == uiconst.UI_MOUSEMOVE:
                self.displayManager.OnMouseMoveGlobal(*args)



    def ToggleCamera(self):
        camSvc = sm.GetService('cameraClient')
        currCam = camSvc.GetActiveCamera()
        if currCam.GetBehavior(cameras.CameraSlayBehavior) is None:
            self.SetupCamera()
        else:
            camSvc.PopActiveCamera(transitionBehaviors=[cameras.LinearTransitionBehavior()])



    def SetupCamera(self):
        camService = sm.GetService('cameraClient')
        currCam = camService.GetActiveCamera()
        if currCam.GetBehavior(cameras.CameraSlayBehavior) is None:
            slayCamera = cameras.CameraSlay(math.pi / 2.0, math.pi)
            slayCamera.SetPointOfInterest((self.placeableLocation.x, self.placeableLocation.y + SLAY_TABLE_HEIGHT, self.placeableLocation.z))
            slayBehaviour = cameras.CameraSlayBehavior(slayCamera.poi)
            slayCamera.AddBehavior(slayBehaviour)
            camService.PushActiveCamera(slayCamera, transitionBehaviors=[cameras.LinearTransitionBehavior()])



    def CreateSetupUI(self):
        if not self.setupManager or self.setupManager.dead:
            self.SetupCamera()
            self.setupManager = sm.GetService('window').GetWindow('SlaySetup', decoClass=minigames.SlaySetupGUI, create=1)
            self.setupManager.SetConfig(util.KeyVal(dictLikeObject=self.gameConfiguration.state), self)
            self.playing = True



    def CreatePlayUI(self):
        if not self.displayManager:
            self.displayManager = sm.GetService('window').GetWindow('SlayGUI', decoClass=minigames.SlayGUI, create=1)
            self.displayManager.placeableLocation = util.KeyVal(x=self.placeableLocation.x, y=self.placeableLocation.y, z=self.placeableLocation.z)
            self.displayManager.SetConfig(util.KeyVal(dictLikeObject=self.gameConfiguration.state), self)
            self.displayManager.modelsManager = self.modelsManager



    def CancelRunningBet(self):
        self.runningBet = None
        self.Action(slayConst.CANCEL_RUNNING_BET)



    def SubmitRunningBet(self, amount):
        self.runningBet = None
        self.Action(slayConst.PLACE_RUNNING_BET, amount)



    def OnMinigameServerMessage(self, entityID, *args):
        event = args[0]
        if event == slayConst.RUNNING_BET_SETUP:
            self.runningBet = sm.GetService('window').GetWindow('SlayRunningBetGUI', decoClass=minigames.SlayRunningBetGUI, create=1)
            maxBetAmount = args[1]
            playerInGamePoints = args[2]
            self.runningBet.SetConfig(maxBetAmount, playerInGamePoints, self)
        elif event == slayConst.KICKOUT_DUE_TO_SETUP_INACTIVITY:
            self.ResetState()
            eve.Message('CustomInfo', {'info': mls.UI_MINIGAME_KICKOUT_DUE_TO_SETUP_INACTIVITY})
        elif event == slayConst.SLOT_POSITION_UPDATE:
            pos = args[1]
            self.WalkTo(pos, args)
        elif event == slayConst.GENERIC_MESSAGE:
            eve.Message('CustomInfo', {'info': slayConst.slayMessageMapping[args[1]]})
        elif event == slayConst.IN_GAME_MESSAGE:
            msg = slayConst.slayMessageMapping[args[1]]
            if len(args) > 3:
                msg = msg % args[3]
            self.ShowMessage(msg, args[2])
        elif event == slayConst.KICKOUT_DUE_TO_INACTIVITY:
            self.ResetState()
            eve.Message('CustomInfo', {'info': mls.UI_MINIGAME_INACTIVITY_KICKOUT % {'min': str(self.gameConfiguration.inactivityKickoutLimitSeconds / 60)}})
        elif event == slayConst.CHAT_CHANNEL_JOIN:
            channelID = args[1]
            chat = sm.GetService('LSC')
            chat.JoinChannel(channelID)
        elif event == slayConst.CHAT_CHANNEL_LEAVE:
            channelID = args[1]
            chat = sm.GetService('LSC')
            chat.LeaveChannel(channelID)
        elif event in (slayConst.LEAVE_GAME_PROCESSED, slayConst.MINIGAME_SYSTEM_SHUTDOWN):
            self.ResetState()
        elif event == slayConst.LIGHT_STATE_UPDATE:
            self.lightsState = args[1]
            self.modelsManager.UpdateLights(self.lightsState)
        elif event == slayConst.ACTIVATE_LIGHT:
            self.modelsManager.SetSlotHighlight(args[1])
        elif event == slayConst.REQUEST_RUNNING_BET:
            bettingArgs = args[1]
            betStarterName = bettingArgs[0]
            betAmount = bettingArgs[1]
            ret = eve.Message('CustomQuestion', {'header': mls.UI_MINIGAME_RUNNING_BET_CHALLENGE,
             'question': mls.UI_MINIGAME_RUNNING_BET_CHALLENGE_STARTED % {'name': betStarterName,
                          'amount': util.FmtISK(betAmount)}}, uiconst.YESNO)
            if ret == uiconst.ID_YES:
                self.Action(slayConst.ACCEPT_RUNNING_BET_CHALLENGE)
            else:
                self.displayManager.Close()
        elif event == slayConst.ACCESS_DENY_SETTING_UP:
            if self.setupManager:
                self.setupManager.CloseQuietly()
                self.setupManager = None
                self.gameui.MessageBox(mls.UI_MINIGAME_CANT_START_GAME_BEING_SET_UP, mls.UI_MINIGAME_FAILED_TO_JOIN)
        elif event == slayConst.SPECTATE_MODE:
            self.ToggleCamera()
        elif event == slayConst.GAMEMASTER_INIT:
            self.CreateSetupUI()
            self.inUse = True
            self.exiting = False
            self.joined = True
            self.gameMasterInit = True
            self.setupManager.ShowGameMasterSetup()
            self.currPlayerID = session.charid
        elif event == slayConst.UPDATE_AVAILABLE_COLORS:
            if self.setupManager:
                self.setupManager.UpdateAvailableColors(args[1])
        elif event == slayConst.GAME_INIT:
            self.exiting = False
            self.CreateSetupUI()
            self.setupManager.ShowJoinGame(args[1])
        elif event in [slayConst.ACCESS_GRANT_WAITING, slayConst.ACCESS_GRANT_WELCOMEBACK, slayConst.ACCESS_GRANT_STARTING_NOW]:
            self.inUse = True
            self.gameMasterSettings = args[1]
            self.RecordGameStatus()
            if self.setupManager:
                self.setupManager.CloseQuietly()
            self.setupManager = None
            self.CreatePlayUI()
            self.displayManager.GetChart(self.recordedGame)
            self.exiting = False
            self.joined = True
            self.displayManager.ClearInfo()
            self.displayManager.ShowInfo(None, None, self.recordedGame)
            self.tableData = None
            if event == slayConst.ACCESS_GRANT_WAITING:
                welcomeMessage = mls.UI_MINIGAME_WELCOME % {'playerNumber': args[2],
                 'playersNeeded': args[3]}
                self.ShowMessage(welcomeMessage, minigameConst.MESSAGE_NORMAL)
            elif event == slayConst.ACCESS_GRANT_WELCOMEBACK:
                self.ShowMessage(mls.UI_MINIGAME_WELCOME_BACK, minigameConst.MESSAGE_NORMAL)
        elif event == slayConst.GAME_RESTART:
            if len(args) > 1:
                self.ShowMessage(mls.UI_MINIGAME_CANNOT_JOIN % {'reason': args[1]}, minigameConst.MESSAGE_ERROR)
        elif event == slayConst.CLEAR_TABLE:
            self.ResetTable()
        elif event == slayConst.GAME_CLOSED:
            self.ResetState()
        elif event == slayConst.GAME_WON_BY_AI:
            potSum = int(args[1])
            if potSum > 0:
                self.gameui.MessageBox(mls.UI_MINIGAME_YOU_LOST_TO_AI % {'amount': util.FmtISK(potSum)}, mls.UI_MINIGAME_YOU_LOST_CAPTION)
            else:
                self.gameui.MessageBox(mls.UI_MINIGAME_YOU_LOST_OTHER_WON_TO_AI, mls.UI_MINIGAME_YOU_LOST_CAPTION)
            self.ResetState(True)
        elif event == slayConst.GAME_WON:
            playerID = int(args[1])
            winnerName = str(args[2])
            potSum = int(args[3])
            if playerID == session.charid:
                self.PlaySound(slayConst.SOUND_PLAYER_WON)
                if potSum > 0:
                    self.gameui.MessageBox(mls.UI_MINIGAME_YOU_WON % {'amount': util.FmtISK(potSum)}, mls.UI_MINIGAME_YOU_WON_CAPTION)
                else:
                    self.gameui.MessageBox(mls.UI_MINIGAME_YOU_WON_SIMPLE, mls.UI_MINIGAME_YOU_WON_CAPTION)
            elif potSum > 0:
                self.gameui.MessageBox(mls.UI_MINIGAME_YOU_LOST % {'name': winnerName,
                 'amount': util.FmtISK(potSum)}, mls.UI_MINIGAME_YOU_LOST_CAPTION)
            else:
                self.gameui.MessageBox(mls.UI_MINIGAME_YOU_LOST_OTHER_WON % {'name': winnerName}, mls.UI_MINIGAME_YOU_LOST_CAPTION)
            self.ResetState(True)
        elif event == slayConst.READY_PLAY:
            self.ShowMessage(mls.UI_MINIGAME_YOUR_TURN, minigameConst.MESSAGE_NORMAL)
            self.PlaySound(slayConst.SOUND_NOTIFY_YOUR_TURN)
            self.AnalysePlayerSituation()
            self.currPlayerID = session.charid
            self.CreatePlayUI()
            self.modelsManager.Refresh(self.tableData, self.selectedAreaID, self.areaEconomics, self.currPlayerID, self.enemyActivities)
        elif event in (slayConst.READY_WAIT, slayConst.READY_WAIT_FOR_AI):
            self.CreatePlayUI()
            self.displayManager.ResetHighlights()
            if event == slayConst.READY_WAIT_FOR_AI:
                self.currAvatarName = mls.UI_MINIGAME_AI_PLAYER_NAME
                self.ShowMessage(mls.UI_MINIGAME_WAITING_ON_AI, minigameConst.MESSAGE_NORMAL)
            else:
                self.currAvatarName = args[1]
                self.ShowMessage(mls.UI_MINIGAME_WAITING_ON_SPECIFIC_PLAYER % {'name': self.currAvatarName}, minigameConst.MESSAGE_NORMAL)
            self.currPlayerID = None
            self.joined = True
        elif event == slayConst.ROUND_END:
            self.RecordGameStatus()
            self.CreatePlayUI()
            self.displayManager.GetChart(self.recordedGame)
            self.enemyActivities = util.KeyVal(moves=[], upgrades=[])
        elif event == slayConst.PLAYER_LEFT:
            pass
        elif event == slayConst.ACCEPTING_PLAYERS:
            if args[1] == self.entityID:
                self.modelsManager.StartFlashing()
        elif event == slayConst.MEMBERS:
            pass
        elif event == slayConst.PLAYER_LOST:
            entityID = args[1]
            if entityID == self.entityID:
                self.gameui.MessageBox(mls.UI_MINIGAME_SORRY_YOU_LOST, mls.UI_MINIGAME_YOU_LOST_CAPTION)
                self.ResetState(True)
        elif event == slayConst.GAME_CANCELED:
            entityID = args[1]
            if self.setupManager is not None:
                self.modelsManager.StopFlashing()
                self.setupManager.Close()
                self.setupManager = None
            elif self.joined:
                self.ResetState(False)
        elif event == slayConst.REFRESH_DATA:
            self.modelsManager.StopFlashing(clearTiles=False)
            fresh = self.tableData is None
            newMap = {}
            if fresh:
                newMap = args[1]
            else:
                for key in self.tableData:
                    newMap[key] = self.tableData[key]

                for key in args[1]:
                    newTile = slaycommon.SlayTile()
                    newTile.FromRaw(args[1][key])
                    newMap[newTile.tileID] = args[1][key]

            if self.playing:
                self.compiledMap.LoadMapFromRaw(newMap, self.gameMasterSettings.xSize, self.gameMasterSettings.ySize)
            activities = self.HighlightEnemyActivities(self.tableData, newMap)
            self.ConstructSoundEvents(self.tableData, newMap)
            if activities is not None:
                if len(activities.moves) > 0:
                    self.enemyActivities.moves.append(activities.moves)
                elif len(activities.upgrades) > 0:
                    self.enemyActivities.upgrades = activities.upgrades
            self.tableData = newMap
            if not self.joined:
                self.modelsManager.Refresh(self.tableData, enemyActivitiesHighlighting=self.enemyActivities)
            else:
                self.CreatePlayUI()
                self.displayManager.doNotFade = True
                if fresh:
                    if self.joined and self.introDone == False:
                        self.introDone = True
                        self.displayManager.SetBanner(self.GetMyColor())
                        self.RecordGameStatus()
                        self.displayManager.GetChart(self.recordedGame)
                self.displayManager.storedTableData = self.tableData
                economics = None
                if self.joined == True:
                    if self.infoToDisplay is not None and self.infoToDisplay in self.areaEconomics:
                        economics = self.areaEconomics[self.infoToDisplay]
                        self.selectedAreaID = self.infoToDisplay
                        self.displayManager.ShowInfo(economics, self.CalculateAvailableUnits(economics.saved), self.recordedGame)
                        self.infoToDisplay = None
                    elif self.selectedAreaID is not None and self.selectedAreaID in self.areaEconomics:
                        economics = self.areaEconomics[self.selectedAreaID]
                        self.displayManager.ShowInfo(economics, self.CalculateAvailableUnits(economics.saved), self.recordedGame)
                    if economics:
                        self.displayManager.ShowInfo(economics, self.CalculateAvailableUnits(economics.saved), self.recordedGame)
                    else:
                        self.displayManager.ShowInfo(None, None, self.recordedGame)
                self.modelsManager.Refresh(self.tableData, self.selectedAreaID, self.areaEconomics, self.currPlayerID, self.enemyActivities)
        elif event == slayConst.AREA_INFO:
            key = args[1]
            economics = args[2]
            self.areaEconomics[key] = economics
            self.CreatePlayUI()
            self.modelsManager.Refresh(self.tableData, self.selectedAreaID, self.areaEconomics, self.currPlayerID, self.enemyActivities)
        elif event == slayConst.AREA_INFO_AGGREGATED:
            listOfInfo = args[1]
            for entry in listOfInfo:
                key = entry[0]
                economics = entry[1]
                self.areaEconomics[key] = economics

            self.CreatePlayUI()
            self.modelsManager.Refresh(self.tableData, self.selectedAreaID, self.areaEconomics, self.currPlayerID, self.enemyActivities)
        elif event == slayConst.KILL_UNIT:
            pass
        elif event == slayConst.AREAS_MERGED:
            selectedArea = args[1]
            deletedArea = args[2]
            newEconomics = args[3]
            self.areaEconomics[selectedArea] = newEconomics
            self.selectedAreaID = selectedArea
            self.infoToDisplay = selectedArea
            self.CreatePlayUI()
            self.modelsManager.Refresh(self.tableData, self.selectedAreaID, self.areaEconomics, self.currPlayerID, self.enemyActivities)
            if self.areaEconomics.has_key(deletedArea):
                del self.areaEconomics[deletedArea]
        elif event == slayConst.RESET_TIMER:
            timerMode = args[2]
            if timerMode == minigameConst.TIMER_MODE_DELAYTIMER:
                timePart = args[4]
                if timePart == minigameConst.TIMER_DELAYTIME:
                    self.displayManager.ResetTurnCounter(timerMode, args[3], timePart=timePart, mainTime=args[5])
                else:
                    self.displayManager.ResetTurnCounter(timerMode, args[3], timePart=timePart)
            else:
                self.displayManager.ResetTurnCounter(timerMode, args[3])
        else:
            raise RuntimeError('Minigame (%s) got unrecognised server message: %s. *args is: %s' % (self.__class__.__name__, event, args))



    def MakeMapDict(self, map):
        lookup = {}
        for subRow in map:
            for rawTile in subRow:
                subTile = slaycommon.SlayTile()
                subTile.FromRaw(rawTile)
                lookup[subTile.tileID] = rawTile


        return lookup



    def ConstructSoundEvents(self, oldTable, newTable):
        if not oldTable:
            return 
        for key in oldTable:
            oldTile = slaycommon.SlayTile()
            oldTile.FromRaw(oldTable[key])
            newTile = slaycommon.SlayTile()
            newTile.FromRaw(newTable[oldTile.tileID])
            if oldTile.occupier.unitID == slayConst.OCCUPY_NONE:
                if newTile.occupier.unitID == slayConst.OCCUPY_PEASANT:
                    self.PlaySound(slayConst.SOUND_MOVE_PEASANT)
                elif newTile.occupier.unitID == slayConst.OCCUPY_SPEARMAN:
                    self.PlaySound(slayConst.SOUND_MOVE_SPEARMAN)
                elif newTile.occupier.unitID == slayConst.OCCUPY_KNIGHT:
                    self.PlaySound(slayConst.SOUND_MOVE_KNIGHT)
                elif newTile.occupier.unitID == slayConst.OCCUPY_BARON:
                    self.PlaySound(slayConst.SOUND_MOVE_BARON)
            if oldTile.owner == session.charid:
                if oldTile.occupier.unitID in [slayConst.OCCUPY_PEASANT,
                 slayConst.OCCUPY_SPEARMAN,
                 slayConst.OCCUPY_KNIGHT,
                 slayConst.OCCUPY_BARON]:
                    if oldTile.occupier.strength < newTile.occupier.strength:
                        self.PlaySound(slayConst.SOUND_UPGRADE_UNIT)
            if oldTile.owner != newTile.owner:
                if oldTile.occupier.unitID == slayConst.OCCUPY_PEASANT:
                    self.PlaySound(slayConst.SOUND_KILL_PEASANT)
                elif oldTile.occupier.unitID == slayConst.OCCUPY_SPEARMAN:
                    self.PlaySound(slayConst.SOUND_KILL_SPEARMAN)
                elif oldTile.occupier.unitID == slayConst.OCCUPY_KNIGHT:
                    self.PlaySound(slayConst.SOUND_KILL_KNIGHT)
                elif oldTile.occupier.unitID == slayConst.OCCUPY_TOWN:
                    self.PlaySound(slayConst.SOUND_KILL_TOWN)
            if oldTile.occupier.unitID == slayConst.OCCUPY_PINEFOREST and newTile.occupier.unitID != slayConst.OCCUPY_PINEFOREST:
                self.PlaySound(slayConst.SOUND_KILL_PINEFOREST)
            elif oldTile.occupier.unitID == slayConst.OCCUPY_PALMFOREST and newTile.occupier.unitID != slayConst.OCCUPY_PALMFOREST:
                self.PlaySound(slayConst.SOUND_KILL_PALMFOREST)




    def HighlightEnemyActivities(self, oldTable, newTable):
        if not oldTable:
            return 
        moves = []
        upgrades = []
        for key in oldTable:
            oldTile = slaycommon.SlayTile()
            oldTile.FromRaw(oldTable[key])
            if self.HasUnit(oldTile):
                newTileRaw = newTable[oldTile.tileID]
                newTile = slaycommon.SlayTile()
                newTile.FromRaw(newTileRaw)
                if not slaycommon.IsAIPlayer(newTile.owner) and newTile.owner != session.charid:
                    if newTile.occupier.ID != oldTile.occupier.ID:
                        moves.append(newTile)
                    elif newTile.occupier.unitID != oldTile.occupier.unitID:
                        upgrades.append(newTile)

        for key in newTable:
            newTile = slaycommon.SlayTile()
            newTile.FromRaw(newTable[key])
            if newTile.tileID not in oldTable:
                continue
            if self.HasUnit(newTile):
                oldTileRaw = oldTable[newTile.tileID]
                oldTile = slaycommon.SlayTile()
                oldTile.FromRaw(oldTileRaw)
                if not slaycommon.IsAIPlayer(newTile.owner) and newTile.owner != session.charid:
                    if newTile.occupier.ID != oldTile.occupier.ID:
                        moves.append(oldTile)

        return util.KeyVal(moves=moves, upgrades=upgrades)



    def HasUnit(self, tile):
        return tile.occupier.unitID in [slayConst.OCCUPY_PEASANT,
         slayConst.OCCUPY_SPEARMAN,
         slayConst.OCCUPY_CASTLE,
         slayConst.OCCUPY_KNIGHT,
         slayConst.OCCUPY_BARON]



    def GetMyColor(self):
        for key in self.tableData:
            tile = slaycommon.SlayTile()
            tile.FromRaw(self.tableData[key])
            if tile.owner == session.charid:
                return tile.color

        return slayConst.COLOR_3



    def SortGameStatus(self, x, y):
        number1 = x.name
        if slaycommon.IsAIPlayer(number1):
            number1 = -number1
        number2 = y.name
        if slaycommon.IsAIPlayer(number2):
            number2 = -number2
        return number1 - number2



    def RecordGameStatus(self):
        players = {}
        if self.tableData:
            for key in self.tableData:
                tile = slaycommon.SlayTile()
                tile.FromRaw(self.tableData[key])
                if tile.owner is not None:
                    if tile.owner in players:
                        players[tile.owner].points += 1
                    else:
                        players[tile.owner] = util.KeyVal(points=1, name=tile.owner, color=tile.color)

        line = []
        for key in players:
            line.append(players[key])

        line.sort(self.SortGameStatus)
        if len(self.recordedGame[0]) == 0:
            self.recordedGame = [line]
        else:
            self.recordedGame.append(line)



    def AnalysePlayerSituation(self):
        if self.tableData is None:
            return 
        if self.gameScore is None:
            self.gameScore = 0
            for key in self.tableData:
                tile = slaycommon.SlayTile()
                tile.FromRaw(self.tableData[key])
                if tile.owner == session.charid:
                    self.gameScore += 1

        else:
            tempScore = 0
            for key in self.tableData:
                tile = slaycommon.SlayTile()
                tile.FromRaw(self.tableData[key])
                if tile.owner == session.charid:
                    tempScore += 1

            self.gameScore = tempScore



    def ShowMessage(self, message, messageType):
        if self.displayManager:
            self.displayManager.AddMessage(message, messageType)



    def ShowHelp(self):
        sm.GetService('window').GetWindow('SlayInstructions', decoClass=minigames.SlayInstructionsGUI, create=1)



    def CalcPossibleMoves(self, tileX, tileY, unitStrength = None):
        theTile = self.compiledMap.GetTile(tileX, tileY)
        if not theTile.active:
            return 
        if not unitStrength:
            unitStrength = theTile.occupier.strength
        neighbouringTiles = self.compiledMap.GetAreaNeighbours(theTile.areaKey)
        finalPossibleMoves = []
        for tile in neighbouringTiles:
            strongerUnitPresent = False
            for surroundingTile in tile.GetNeighbours():
                if surroundingTile.owner != session.charid:
                    if surroundingTile.occupier.strength >= unitStrength and tile.areaKey == surroundingTile.areaKey:
                        strongerUnitPresent = True
                        break

            if not strongerUnitPresent and tile.occupier.strength < unitStrength:
                finalPossibleMoves.append(tile.tileID)

        self.modelsManager.SetPossibleMovesHighlight(finalPossibleMoves)



    def CalcPossibleMovesUsingCurrSelectedArea(self):
        if self.selectedAreaID:
            for key in self.compiledMap.tiles:
                if self.compiledMap.tiles[key].areaKey == self.selectedAreaID and self.compiledMap.tiles[key].active:
                    self.CalcPossibleMoves(self.compiledMap.tiles[key].x, self.compiledMap.tiles[key].y, unitStrength=slaycommon.SlayUnit(slayConst.OCCUPY_PEASANT).strength)
                    break




    def TileClick(self, tileX, tileY):
        if self.tableData is None:
            return 
        if self.currPlayerID != session.charid:
            if len(self.currAvatarName) == 0:
                self.ShowMessage(mls.UI_MINIGAME_WAITING_ON_AI, minigameConst.MESSAGE_ERROR)
            else:
                self.ShowMessage(mls.UI_MINIGAME_WAITING_ON_SPECIFIC_PLAYER % {'name': self.currAvatarName}, minigameConst.MESSAGE_ERROR)
        found = False
        for key in self.tableData:
            if found:
                break
            useTile = slaycommon.SlayTile()
            useTile.FromRaw(self.tableData[key])
            if useTile.tileID == '%s.%s' % (tileX, tileY) and useTile.owner == session.charid:
                found = True
                break

        if found:
            found = False
            if useTile.areaKey in self.areaEconomics:
                areaSize = 0
                for key in self.tableData:
                    if found:
                        break
                    tempTile = slaycommon.SlayTile()
                    tempTile.FromRaw(self.tableData[key])
                    if tempTile.areaKey == useTile.areaKey:
                        areaSize += 1
                    if areaSize > 1:
                        found = True

                if found == True:
                    economics = self.areaEconomics[useTile.areaKey]
                    self.selectedAreaID = useTile.areaKey
                    self.displayManager.ShowInfo(economics, self.CalculateAvailableUnits(economics.saved), self.recordedGame)
                    if self.currPlayerID == session.charid:
                        self.modelsManager.SetSelectedArea(self.selectedAreaID)



    def CalculateAvailableUnits(self, money):
        available = {}
        if money > 0:
            buyableUnits = (slaycommon.SlayUnit(slayConst.OCCUPY_PEASANT),
             slaycommon.SlayUnit(slayConst.OCCUPY_SPEARMAN),
             slaycommon.SlayUnit(slayConst.OCCUPY_CASTLE),
             slaycommon.SlayUnit(slayConst.OCCUPY_KNIGHT),
             slaycommon.SlayUnit(slayConst.OCCUPY_BARON))
            for unit in buyableUnits:
                if unit.buyCost > 0:
                    numAvailable = money / unit.buyCost
                    if numAvailable > 0:
                        available[unit.unitID] = numAvailable

        return available



    def AddUnit(self, x, y, unitID):
        if unitID == slayConst.OCCUPY_PEASANT:
            if self.selectedAreaID:
                self.Action(slayConst.PLACE_UNIT, (x, y))
            else:
                self.ShowMessage(mls.UI_MINIGAME_PICK_REGION, minigameConst.MESSAGE_ERROR)
        elif unitID == slayConst.OCCUPY_CASTLE:
            self.Action(slayConst.PLACE_CASTLE, (x, y))
        else:
            raise RuntimeError("Illegal move, can't add unit with ID %s" % unitID)



    def MoveUnit(self, fromX, fromY, toX, toY):
        self.Action(slayConst.MOVE_UNIT, (fromX,
         fromY,
         toX,
         toY))



    def EndTurn(self):
        self.Action(slayConst.NEXT_TURN)



    def LeaveGame(self):
        self.ResetState()



    def DelayedExitAnimation(self):
        pass



    def ResetState(self, delayExit = False):
        camSvc = sm.GetService('cameraClient')
        currCam = camSvc.GetActiveCamera()
        if currCam.GetBehavior(cameras.CameraSlayBehavior) is not None:
            camSvc.PopActiveCamera(transitionBehaviors=[cameras.LinearTransitionBehavior()])
        self.exiting = True
        self.playing = False
        self.BindRemoteController()
        uthread.new(self.remoteController.LeaveGame)
        self.inUse = False
        self.joined = False
        self.currAvatarName = ''
        self.introDone = False
        self.selectedAreaID = None
        self.gameMasterSettings = None
        if self.setupManager:
            self.setupManager.CloseQuietly()
        self.setupManager = None
        if self.displayManager:
            self.displayManager.Close()
        self.displayManager = None
        if self.runningBet:
            self.runningBet.Close()
        self.runningBet = None
        self.recordedGame = [[]]
        self.enemyActivities = util.KeyVal(moves=[], upgrades=[])
        uthread.new(self.DelayedExitAnimation)



    def ResetTable(self):
        self.gameScore = None
        self.tableData = None
        self.areaEconomics = {}
        self.modelsManager.ClearTable()
        self.lightsState = LIGHTS_OFF
        self.modelsManager.UpdateLights(self.lightsState)



    def PlaySound(self, soundEvent):
        self.audio.SendUIEvent(soundEvent)



    def Action(self, action, args = None):
        if action == slayConst.PLAYER_LEFT:
            uthread.new(self.SendMessageToServer, action, args)
            self.ResetState(False)
        else:
            uthread.new(self.SendMessageToServer, action, args)




