import service
import blue
import const
import geo2
import GameWorld
import zaction

class ActionObjectSvc(service.Service):
    __guid__ = 'svc.actionObjectSvc'
    __machoresolve__ = 'location'
    __componentTypes__ = ['actionObject']
    __notifyevents__ = ['OnEntityDeleted']

    def __init__(self):
        self.manager = GameWorld.ActionObjectManager()
        self.manager.loadActionObjectDataFunc = self._LoadActionObjectData
        self.manager.loadActionStationGlobalDataFunc = self._LoadActionStationGlobalData
        self.preservedStates = {}
        service.Service.__init__(self)



    def Run(self, *args):
        service.Service.Run(self, *args)



    def CreateComponent(self, name, state):
        actionObj = GameWorld.ActionObject()
        self.preservedStates[actionObj] = state
        return actionObj



    def PrepareComponent(self, sceneID, entityID, component):
        actionObjID = self.preservedStates[component].get('actionObjectUID', None)
        if actionObjID is None:
            self.LogError('Missing ActionObject ID for entity ', entityID, ', expect missing assets!')
            del self.preservedStates[component]
        elif self.InitActionObject(component, int(actionObjID), entityID) is None:
            self.LogError('Error initializing ActionObject for entity ', entityID, ', expect missing assets!')
            del self.preservedStates[component]



    def SetupComponent(self, entity, component):
        if component in self.preservedStates:
            actionStationOccupants = self.preservedStates[component].get('actionStationOccupants', None)
            if actionStationOccupants:
                for (key, val,) in actionStationOccupants.iteritems():
                    self.manager.SetActionStationInUse(component, component.actionStations[key], val)

            del self.preservedStates[component]



    def RegisterComponent(self, entity, component):
        pass



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return None



    def PackUpForClientTransfer(self, component):
        state = {}
        state['actionObjectUID'] = int(component.actionObjectData.UID)
        occupantDict = {}
        for (index, value,) in enumerate(component.actionStations):
            occupantDict[index] = value.occupant

        state['actionStationOccupants'] = occupantDict
        return state



    def UnRegisterComponent(self, entity, component):
        self.manager.RemoveActionObject(component)



    def OnEntityDeleted(self, entityID, sceneID):
        self.manager.StopUsingActionObject(entityID)



    def InitActionObject(self, actionObject, actionObjectUID, entID):
        aoData = self.manager.GetActionObjectData(actionObjectUID)
        if aoData is None:
            self.LogError('Could not look up ActionObjectData for ActionObject with UID ' + str(actionObjectUID) + '.')
            return 
        actionObject.Init(aoData, entID)
        self.manager.AddActionObject(actionObject)
        return actionObject



    def _LoadActionObjectData(self, actionObjectUID):
        aoDbData = self.GetActionObjectRecord(actionObjectUID)
        if aoDbData is None:
            return 
        aoData = GameWorld.ActionObjectData(actionObjectUID, str(aoDbData['Name']))
        if self._LoadExitPoints(aoData) is False:
            return 
        if self._LoadActionStationLocalData(aoData) is False:
            return 
        self.manager.AddActionObjectData(aoData)
        return aoData



    def _LoadExitPointsToList(self, rows, destList):
        if rows is None:
            return True
        for row in rows:
            exitPoint = GameWorld.ActionExitPoint(row['pos'], row['rot'])
            destList.append(exitPoint)

        return True



    def _LoadExitPoints(self, aoData):
        globalExitRows = self.GetActionObjectExits(aoData.UID, 0)
        return self._LoadExitPointsToList(globalExitRows, aoData.exitPoints)



    def _LoadActionStationLocalData(self, aoData):
        asMappingRows = self.GetActionObjectStations(aoData.UID)
        for asMapping in asMappingRows:
            asGlobalData = self.manager.GetActionStationGlobalData(asMapping['StationID'])
            asLocalData = GameWorld.ActionStationLocalData(asGlobalData, asMapping['pos'], asMapping['rot'])
            if self._LoadActionStationExitPoints(asLocalData, aoData.UID, asMapping['InstID']) is False:
                return False
            aoData.actionStationLocalDatas.append(asLocalData)

        return True



    def _LoadActionStationExitPoints(self, asLocalData, aoUID, asInstanceID):
        asExitPointRows = self.GetActionObjectExits(aoUID, asInstanceID)
        return self._LoadExitPointsToList(asExitPointRows, asLocalData.exitPoints)



    def _LoadActionStationGlobalData(self, asUID):
        asDbData = self.GetActionStationRecord(asUID)
        if asDbData is None:
            return 
        asGlobalData = GameWorld.ActionStationGlobalData(asUID)
        if self._LoadActionEntries(asGlobalData) is False:
            return 
        self.manager.AddActionStationGlobalData(asGlobalData)
        return asGlobalData



    def _LoadActionEntries(self, asGlobalData):
        actionMappingRows = self.GetActionStationActions(asGlobalData.UID)
        for action in actionMappingRows:
            tagList = ''
            entry = None
            for potentialMatch in asGlobalData.actionEntries:
                if potentialMatch.MatchEntTags(tagList):
                    entry = potentialMatch
                    break

            if entry is None:
                entry = GameWorld.ActionEntry(tagList)
                asGlobalData.actionEntries.append(entry)
            entry.AddAction(action)

        return True



    def _PrepareActionObject(self, ent, staticObject, position, rotation):
        pass



    def GetActionObjectRecord(self, actionObjectID):
        if actionObjectID is not None:
            aoRow = cfg.actionObjects.Get(actionObjectID)
            if aoRow is not None:
                return {'ID': aoRow.actionObjectID,
                 'Name': aoRow.actionObjectName}



    def GetActionStationRecord(self, actionStationTypeID):
        if actionStationTypeID is not None:
            asRow = cfg.actionStations.Get(actionStationTypeID)
            if asRow is not None:
                return {'ID': asRow.actionStationTypeID,
                 'Name': asRow.actionStationTypeName}



    def GetActionStationActions(self, actionStationTypeID):
        rows = cfg.actionStationActions.get(actionStationTypeID)
        actions = []
        if rows is not None:
            for row in rows:
                actions.append(row.actionID)

        return actions



    def GetActionObjectStations(self, actionObjectID):
        rows = cfg.actionObjectStations.get(actionObjectID)
        stations = []
        if rows is not None:
            for row in rows:
                quat = geo2.QuaternionRotationSetYawPitchRoll(row.rotX, row.rotY, row.rotZ)
                pos = (row.posX, row.posY, row.posZ)
                stations.append({'StationID': row.actionStationTypeID,
                 'InstID': row.actionStationInstanceID,
                 'pos': pos,
                 'rot': quat})

        return stations



    def GetActionObjectExits(self, actionObjectID, actionStationInstanceID):
        exits = []
        aoRows = cfg.actionObjectExits.get(actionObjectID)
        if aoRows is not None:
            rows = aoRows.get(actionStationInstanceID)
            if rows is not None:
                for row in rows:
                    quat = geo2.QuaternionRotationSetYawPitchRoll(row.rotX, row.rotY, row.rotZ)
                    pos = (row.posX, row.posY, row.posZ)
                    exits.append({'pos': pos,
                     'rot': quat})

        return exits



exports = {'actionProcTypes.UseActionObject': zaction.ProcTypeDef(isMaster=True, procCategory='ActionObject', properties=[zaction.ProcPropertyTypeDef('Distance', 'F', userDataType=None, isPrivate=False)]),
 'actionProcTypes.StopUsingActionObject': zaction.ProcTypeDef(isMaster=True, procCategory='ActionObject'),
 'actionProcTypes.IsActionObjectActionAvailable': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='ActionObject', properties=[zaction.ProcPropertyTypeDef('Distance', 'F', userDataType=None, isPrivate=False)]),
 'actionProcTypes.ExclusiveIsActionObjectActionAvailable': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='ActionObject', properties=[zaction.ProcPropertyTypeDef('Distance', 'F', userDataType=None, isPrivate=False)]),
 'actionProcTypes.SetActionObjectEntry': zaction.ProcTypeDef(isMaster=False, procCategory='ActionObject'),
 'actionProcTypes.GetActionStationPosRot': zaction.ProcTypeDef(isMaster=False, procCategory='ActionObject'),
 'actionProcTypes.IsEntityOnActionObject': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='ActionObject')}

