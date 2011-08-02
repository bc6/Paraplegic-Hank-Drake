import GameWorld
import blue
import service
import collections
import geo2

class PerceptionComponent:
    __guid__ = 'AI.PerceptionComponent'

    def __init__(self, state):
        self.state = state




class perceptionCommon(service.Service):
    __guid__ = 'AI.perceptionCommon'
    sceneManagers = {}
    settings = None
    __componentTypes__ = ['perception']

    def CreateComponent(self, name, state):
        return PerceptionComponent(state)



    def PrepareComponent(self, sceneID, entityID, component):
        if sceneID not in self.sceneManagers:
            self.LogError('SceneID in prepare perception component has no previous manager ', sceneID, entityID)
            return 



    def SetupComponent(self, entity, component):
        pass



    def RegisterComponent(self, entity, component):
        if entity.scene.sceneID not in self.sceneManagers:
            self.LogError("Trying to register a perception component thats doesn't have a valid scene", entity.entityID)
            return 
        entityTypeID = None
        entityType = component.state.get(const.perception.PERCEPTION_COMPONENT_ENTITY_TYPE)
        if entityType:
            entityTypeID = const.perception.PERCEPTION_ENTITY_TYPE_TO_ID.get(entityType)
        if not entityTypeID:
            self.LogError('entity in prepare perception component has invalid entityType', entity.entityID)
            return 
        behaviorSensesID = component.state.get(const.perception.PERCEPTION_COMPONENT_SENSE_GROUP)
        behaviorFiltersID = component.state.get(const.perception.PERCEPTION_COMPONENT_FILTER_GROUP)
        behaviorDecaysID = component.state.get(const.perception.PERCEPTION_COMPONENT_DECAY_GROUP)
        if behaviorSensesID is None or behaviorFiltersID is None or behaviorDecaysID is None:
            self.LogError('entity in prepare perception component has missing state behaviorIDs', entity.entityID)
            return 
        sensorBoneName = component.state.get(const.perception.PERCEPTION_COMPONENT_SENSOR_BONENAME)
        sensorOffsetString = component.state.get(const.perception.PERCEPTION_COMPONENT_SENSOR_OFFSET)
        sensorOffset = geo2.Vector(0.0, 0.0, 0.0)
        if sensorBoneName is None and sensorOffsetString is None:
            bv = entity.GetComponent('boundingVolume')
            if bv is not None:
                sensorOffset = geo2.Vector(*bv.minExtends)
                sensorOffset.x = sensorOffset.x + (bv.maxExtends[0] - bv.minExtends[0]) / 2
                sensorOffset.y = sensorOffset.y + (bv.maxExtends[1] - bv.minExtends[1]) / 2
                sensorOffset.z = sensorOffset.z + (bv.maxExtends[2] - bv.minExtends[2]) / 2
        if sensorBoneName is None:
            sensorBoneName = ''
        if sensorOffsetString is not None:
            sensorOffsetString = sensorOffsetString.strip('()')
            sensorOffsetTuple = sensorOffsetString.split(',')
            try:
                sensorOffset = geo2.Vector(float(sensorOffsetTuple[0]), float(sensorOffsetTuple[1]), float(sensorOffsetTuple[2]))
            except:
                self.LogError('entity has invalid perception sensor offset value', entity.entityID)
                sensorOffset = geo2.Vector(0.0, 0.0, 0.0)
        dropStimType = component.state.get(const.perception.PERCEPTION_COMPONENT_DROP_STIMTYPE)
        dropRange = component.state.get(const.perception.PERCEPTION_COMPONENT_DROP_RANGE)
        if dropStimType is None:
            dropStimType = ''
        if dropRange is None:
            dropRange = 0.0
        positionComponent = entity.GetComponent('position')
        perceptionManager = self.sceneManagers[entity.scene.sceneID]
        perceptionManager.AddEntity(entity.entityID, behaviorSensesID, behaviorFiltersID, behaviorDecaysID, entityTypeID, positionComponent, sensorBoneName, sensorOffset.x, sensorOffset.y, sensorOffset.z, dropStimType, dropRange)



    def UnRegisterComponent(self, entity, component):
        if entity.scene.sceneID not in self.sceneManagers:
            self.LogError("Trying to remove a perception entity who's scene doesn't have a manager", entity.entityID)
            return 
        perceptionManager = self.sceneManagers[entity.scene.sceneID]
        perceptionManager.RemoveEntity(entity.entityID)



    def TearDownComponent(self, entity, component):
        pass



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return component.state



    def UnPackFromSceneTransfer(self, component, entity, state):
        component.state = state
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Type'] = component.state.get(const.perception.PERCEPTION_COMPONENT_ENTITY_TYPE)
        if not hasattr(self, 'reportLookupsCreated'):
            self.CreateLookups()
            self.reportLookupsCreated = True
        groupID = component.state.get(const.perception.PERCEPTION_COMPONENT_SENSE_GROUP)
        report['senseGroupID'] = groupID
        if groupID:
            behaviorList = self.behaviorSenses.get(groupID)
            if not behaviorList:
                report['senses'] = 'Invalid group ID'
            else:
                for behaviorSense in behaviorList.values():
                    senseID = behaviorSense[1]
                    sense = self.senses.get(senseID)
                    if sense:
                        senseName = sense[1]
                    else:
                        senseName = 'InvalidSense'
                    reportVal = senseName + '(' + str(senseID) + ')' + ',Los=' + str(sense[2]) + ',Range=' + str(behaviorSense[2]) + ',fovAngle=' + str(behaviorSense[3])
                    report['sense%03d' % senseID] = reportVal

        groupID = component.state.get(const.perception.PERCEPTION_COMPONENT_FILTER_GROUP)
        report['filterGroupID'] = groupID
        if groupID:
            behaviorList = self.behaviorFilters.get(groupID)
            if not behaviorList:
                report['filters'] = 'Invalid group ID'
            else:
                for behaviorFilter in behaviorList.values():
                    genID = behaviorFilter[1]
                    reportVal = 'GenID=' + str(genID)
                    senseID = behaviorFilter[2]
                    sense = self.senses.get(senseID)
                    if sense:
                        senseName = sense[1]
                    else:
                        senseName = 'InvalidSense'
                    reportVal = reportVal + ',' + senseName + '(' + str(senseID) + ')'
                    stimID = behaviorFilter[3]
                    stim = self.stims.get(stimID)
                    if stim:
                        stimName = stim[1]
                    else:
                        stimName = 'InvalidStim'
                    reportVal = reportVal + ',' + stimName + '(' + str(stimID) + ')'
                    subjectID = behaviorFilter[4]
                    subject = self.subjects.get(subjectID)
                    if subject:
                        subjectName = subject[1]
                    else:
                        subjectName = 'InvalidSubject'
                    reportVal = reportVal + ',' + subjectName + '(' + str(subjectID) + ')'
                    candidateID = behaviorFilter[5]
                    candidate = self.candidates.get(candidateID)
                    if candidate:
                        candidateName = candidate[1]
                    else:
                        candidateName = 'InvalidCandidate'
                    reportVal = reportVal + ',' + candidateName + '(' + str(candidateID) + ')'
                    confidenceID = behaviorFilter[6]
                    confidence = self.confidences.get(confidenceID)
                    if confidence:
                        confidenceName = confidence[0]
                    else:
                        confidenceName = 'InvalidConfidence'
                    reportVal = reportVal + ',' + confidenceName + '(' + str(confidenceID) + ')'
                    report['filter%03d' % genID] = reportVal

        groupID = component.state.get(const.perception.PERCEPTION_COMPONENT_DECAY_GROUP)
        report['decayGroupID'] = groupID
        if groupID:
            behaviorList = self.behaviorDecays.get(groupID)
            if not behaviorList:
                report['decays'] = 'Invalid group ID'
            else:
                for behaviorDecay in behaviorList.values():
                    candidateID = behaviorDecay[1]
                    candidate = self.candidates[candidateID]
                    if candidate:
                        candidateName = candidate[1]
                    else:
                        candidateName = 'InvalidCandidate'
                    decayVal = candidateName + '(' + str(candidateID) + ')' + ',Decays=(' + str(behaviorDecay[2]) + ',' + str(behaviorDecay[3]) + ',' + str(behaviorDecay[4]) + ',' + str(behaviorDecay[5]) + ',' + str(behaviorDecay[6]) + ')'
                    report['decay%03d' % candidateID] = decayVal

        manager = self.GetPerceptionManager(entity.scene.sceneID)
        report['Visibility'] = ', '.join([ '%s' % s for s in manager.GetVisibility(entity.entityID) ])
        report['sensor bone name'] = component.state.get(const.perception.PERCEPTION_COMPONENT_SENSOR_BONENAME)
        report['sensor offset'] = component.state.get(const.perception.PERCEPTION_COMPONENT_SENSOR_OFFSET)
        report['drop stimType'] = component.state.get(const.perception.PERCEPTION_COMPONENT_DROP_STIMTYPE)
        report['drop range'] = component.state.get(const.perception.PERCEPTION_COMPONENT_DROP_RANGE)
        return report



    def CreateLookups(self):
        candidateArg = 0
        confidenceArg = 1
        senseArg = 2
        stimArg = 3
        subjectArg = 4
        behaviorSenseArg = 5
        behaviorDecayArg = 6
        behaviorFilterArg = 7
        self.senses = {}
        for sense in self.GetSettings()[senseArg]:
            senseID = sense[0]
            self.senses[senseID] = sense

        self.stims = {}
        for stim in self.GetSettings()[stimArg]:
            stimID = stim[0]
            self.stims[stimID] = stim

        self.candidates = {}
        for candidate in self.GetSettings()[candidateArg]:
            candidateID = candidate[0]
            self.candidates[candidateID] = candidate

        self.subjects = {}
        for subject in self.GetSettings()[subjectArg]:
            subjectID = subject[0]
            self.subjects[subjectID] = subject

        self.confidences = {}
        for confidence in self.GetSettings()[confidenceArg]:
            confidenceID = confidence[1]
            self.confidences[confidenceID] = confidence

        self.behaviorSenses = {}
        for behaviorSense in self.GetSettings()[behaviorSenseArg]:
            groupID = behaviorSense[0]
            if not self.behaviorSenses.get(groupID):
                self.behaviorSenses[groupID] = {}
            senseID = behaviorSense[1]
            self.behaviorSenses[groupID][senseID] = behaviorSense

        self.behaviorFilters = {}
        for behaviorFilter in self.GetSettings()[behaviorFilterArg]:
            groupID = behaviorFilter[0]
            if not self.behaviorFilters.get(groupID):
                self.behaviorFilters[groupID] = {}
            genID = behaviorFilter[1]
            self.behaviorFilters[groupID][genID] = behaviorFilter

        self.behaviorDecays = {}
        for behaviorDecay in self.GetSettings()[behaviorDecayArg]:
            groupID = behaviorDecay[0]
            if not self.behaviorDecays.get(groupID):
                self.behaviorDecays[groupID] = {}
            candidateID = behaviorDecay[1]
            self.behaviorDecays[groupID][candidateID] = behaviorDecay




    def GetPerceptionManager(self, sceneID):
        return self.sceneManagers[sceneID]



    def MakePerceptionManager(self):
        raise NotImplementedError('This is a pure virtual function to create a perception manager')



    def GetSettings(self):
        if not self.settings:
            senses = self.LoadSenses()
            stimTypes = self.LoadStimTypes()
            confidences = self.LoadConfidences()
            candidates = self.LoadCandidates()
            subjects = self.LoadSubjects()
            behaviorSenses = self.LoadBehaviorSenses()
            behaviorDecays = self.LoadBehaviorDecays()
            behaviorFilters = self.LoadBehaviorFilters()
            self.settings = (candidates,
             confidences,
             senses,
             stimTypes,
             subjects,
             behaviorSenses,
             behaviorDecays,
             behaviorFilters)
        return self.settings



    def OnLoadEntityScene(self, sceneID):
        self.LogInfo('Registering a new perception system for scene ', sceneID)
        if sceneID in self.sceneManagers:
            self.LogError('Duplicate scene passed to perception system Register from entityService ', sceneID)
            return 
        perceptionManager = self.MakePerceptionManager()
        self.sceneManagers[sceneID] = perceptionManager
        perceptionManager.SetSceneSettings(self.GetSettings())
        gw = self.gameWorldService.GetGameWorld(sceneID)
        gw.perceptionManager = perceptionManager
        perceptionManager.SetGameWorld(gw)
        perceptionManager.StartTicker(str(sceneID))
        self.LogInfo('Done Creating a new perception system for scene ', sceneID)



    def OnUnloadEntityScene(self, sceneID):
        self.LogInfo('Unloading perception system for scene ', sceneID)
        gw = self.gameWorldService.GetGameWorld(sceneID)
        gw.perceptionManager = None
        if sceneID in self.sceneManagers:
            del self.sceneManagers[sceneID]
        else:
            self.LogError('Non-existent scene passed to perception system Unload from entityService ', sceneID)
        self.LogInfo('Done Unloading perception system for scene ', sceneID)



    def LoadSenses(self):
        self.sensesAllowed = {}
        for senseRow in cfg.perceptionSenses:
            self.sensesAllowed[senseRow.senseID] = (senseRow.senseID, senseRow.senseName, senseRow.losType)

        return tuple(self.sensesAllowed.values())



    def LoadStimTypes(self):
        self.stimTypesAllowed = {}
        for stimTypeRow in cfg.perceptionStimTypes:
            if stimTypeRow.senseID not in self.sensesAllowed:
                self.LogError('AI stimType using non existent senseID ', stimTypeRow)
                continue
            self.stimTypesAllowed[stimTypeRow.stimTypeID] = (stimTypeRow.stimTypeID,
             stimTypeRow.stimTypeName,
             stimTypeRow.createFlag,
             stimTypeRow.rangeDefault,
             stimTypeRow.senseID)

        return tuple(self.stimTypesAllowed.values())



    def LoadConfidences(self):
        self.confidencesAllowed = {}
        for row in const.perception.PERCEPTION_CONFIDENCE_VALUES:
            self.confidencesAllowed[row.confidenceID] = (row.confidenceName, row.confidenceID)

        return tuple(self.confidencesAllowed.values())



    def LoadCandidates(self):
        self.candidatesAllowed = {}
        for row in cfg.perceptionTargets:
            if row.clientServerFlag not in const.perception.PERCEPTION_CLIENTSERVER_FLAGS:
                self.LogError('Perception candidate type has invalid client server flag', row)
                continue
            if self.IsClientServerFlagValid(row.clientServerFlag):
                self.candidatesAllowed[row.targetID] = row.targetName

        return tuple(self.candidatesAllowed.items())



    def LoadSubjects(self):
        self.subjectsAllowed = {}
        for subjectRow in cfg.perceptionSubjects:
            self.subjectsAllowed[subjectRow.subjectID] = subjectRow.subjectName

        return tuple(self.subjectsAllowed.items())



    def LoadBehaviorSenses(self):
        behaviorList = []
        for row in cfg.perceptionBehaviorSenses:
            behaviorList.append((row.behaviorSensesID,
             row.senseID,
             row.range,
             row.fovAngle))

        return tuple(behaviorList)



    def LoadBehaviorDecays(self):
        behaviorList = []
        for row in cfg.perceptionBehaviorDecays:
            if row.targetID in self.candidatesAllowed:
                behaviorList.append((row.behaviorDecaysID,
                 row.targetID,
                 row.decay1,
                 row.decay2,
                 row.decay3,
                 row.decay4,
                 row.decay5))
            elif row.targetID not in cfg.perceptionTargets:
                self.LogError('BehaviorDecay has invalid TargetID', row)

        return tuple(behaviorList)



    def LoadBehaviorFilters(self):
        behaviorList = []
        for row in cfg.perceptionBehaviorFilters:
            if row.targetID in self.candidatesAllowed:
                behaviorList.append((row.behaviorFiltersID,
                 row.filterGenID,
                 row.senseID,
                 row.stimTypeID,
                 row.subjectID,
                 row.targetID,
                 row.confidenceID))
            elif row.targetID not in cfg.perceptionTargets:
                self.LogError('BehaviorFilter has invalid TargetID', row)

        return tuple(behaviorList)



    def GetSensorOffset(self, entity):
        manager = self.GetPerceptionManager(entity.scene.sceneID)
        return manager.GetSensorOffsetByID(entity.entityID)




