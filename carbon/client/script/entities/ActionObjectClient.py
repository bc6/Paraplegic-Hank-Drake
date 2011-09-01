import service
import blue
import const
import geo2
import GameWorld
import svc
import zaction
import cameras

class ActionObjectClientSvc(svc.actionObjectSvc):
    __guid__ = 'svc.actionObjectClientSvc'
    __displayname__ = 'ActionObject Service'
    __machoresolve__ = 'location'
    __dependencies__ = ['cameraClient']
    __notifyevents__ = svc.actionObjectSvc.__notifyevents__[:]
    __notifyevents__.extend(['ProcessSessionChange'])

    def __init__(self):
        svc.actionObjectSvc.__init__(self)
        GameWorld.RegisterPythonActionProc('PerformPythonUICallback', self._PerformUICallback, ('callbackKey',))
        GameWorld.RegisterPythonActionProc('PlayEntityAudio', self._PlayEntityAudio, ('audioName', 'mls', 'TargetList'))
        GameWorld.RegisterPythonActionProc('PlayTutorialVoiceover', self._PlayTutorialVoiceOver, ('messageKey', 'TargetList'))
        GameWorld.RegisterPythonActionProc('PushCameraWithTransition', self._PushCameraWithTransition, ('cameraName', 'behaviorNames', 'transitionSeconds', 'startHeight', 'TargetList'))
        GameWorld.RegisterPythonActionProc('PopCameraWithTransition', self._PopCameraWithTransition, ('transitionSeconds', 'retainYaw', 'retainPitch'))



    def Run(self, *args):
        self.actionObjectServer = None
        svc.actionObjectSvc.Run(self, *args)
        self.zactionClient = sm.GetService('zactionClient')



    def _PushCameraWithTransition(self, cameraName, behaviorNames, transitionSeconds, startHeight, targetList):
        entity = self.entityService.FindEntityByID(targetList[0])
        cameraClass = getattr(cameras, cameraName)
        camera = cameraClass()
        if hasattr(camera, 'SetEntity'):
            camera.SetEntity(entity)
        behaviorClasses = []
        names = behaviorNames.split(',')
        for name in names:
            name = name.replace(' ', '')
            behaviorClass = getattr(cameras, name)
            behavior = behaviorClass()
            if hasattr(behavior, 'SetEntity'):
                behavior.SetEntity(entity)
            if hasattr(behavior, 'pushUp'):
                behavior.pushUp = startHeight
            camera.AddBehavior(behavior)

        transition = cameras.LinearTransitionBehavior(transitionSeconds=float(transitionSeconds))
        self.cameraClient.PushActiveCamera(camera, transitionBehaviors=[transition])
        return True



    def _PopCameraWithTransition(self, transitionSeconds, retainYaw, retainPitch):
        activeCamera = self.cameraClient.GetActiveCamera()
        cameraStack = self.cameraClient.GetCameraStack()
        comingActiveCamera = cameraStack[-2]
        if retainYaw:
            comingActiveCamera.SetYaw(activeCamera.yaw)
        if retainPitch:
            comingActiveCamera.SetPitch(activeCamera.pitch)
        transition = cameras.LinearTransitionBehavior(transitionSeconds=float(transitionSeconds))
        self.cameraClient.PopActiveCamera(transitionBehaviors=[transition])
        return True



    def _PerformUICallback(self, callbackKey):
        raise NotImplementedError('Each game must implement a _PerformUICallback that works with its UI.')



    def _PlayEntityAudio(self, audioName, mls, targetList):
        if mls:
            message = cfg.GetMessage(audioName)
            audioName = message.audio
            if audioName.startswith('wise:/'):
                audioName = audioName[6:]
        for entityID in targetList:
            entity = self.entityService.FindEntityByID(entityID)
            audioComponent = entity.GetComponent('audioEmitter')
            if audioComponent:
                audioComponent.emitter.SendEvent(unicode(audioName))
            else:
                self.LogWarn('Entity with ID %s has no audio component. Audio file %s cannot be played from this entity.' % (entityID, audioName))

        return True



    def _PlayTutorialVoiceOver(self, messageKey, targetList):
        sm.GetService('tutorial').Action_Play_MLS_Audio(messageKey)
        return True



    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change:
            if self.actionObjectServer is None:
                self.actionObjectServer = sm.RemoteSvc('actionObjectServerSvc')



    def GetActionList(self, entID, objectID):
        returnDict = {}
        actionList = self.manager.GetAllAvailableActions(objectID)
        if actionList is not None and len(actionList) > 0:
            tree = self.zactionClient.GetActionTree()
            entity = self.entityService.FindEntityByID(entID)
            treeInst = entity.GetComponent('action').treeInstance
            for action in actionList:
                returnDict[action] = []
                fallbackText = tree.GetTreeNodeByID(action).name
                translatedName = self.GetActionNodeTranslatedText(action, fallbackText)
                returnDict[action].append(translatedName)
                returnDict[action].append(treeInst.IsActionAvailable(action, {'TargetList': [objectID]}))

        return returnDict



    def IsEntityUsingActionObject(self, entID):
        return self.manager.IsEntityUsingActionObject(entID)



    def ExitActionObject(self, entID):
        aoEntID = self.manager.GetAOEntIDUsedByEntity(entID)
        if aoEntID:
            actionList = self.GetActionList(entID, aoEntID)
            if len(actionList) > 0:
                for (actionID, actionData,) in actionList.items():
                    if 'Stand' in actionData[0] and actionData[1] is True:
                        self.TriggerActionOnObject(entID, aoEntID, actionID)
                        return 




    def TriggerActionOnObject(self, entID, targetID, actionID):
        self.zactionClient.StartAction(entID, actionID, {'TargetList': [targetID]})



    def TriggerDefaultActionOnObject(self, entID, targetID):
        actionList = self.GetActionList(entID, targetID)
        if not actionList:
            return 
        isEnabled = False
        for (actionID, actionData,) in actionList.items():
            if actionData[1] is True:
                isEnabled = True
                defaultActionID = actionID
                break

        if isEnabled:
            self.TriggerActionOnObject(entID, targetID, defaultActionID)



exports = {'actionProcTypes.PerformPythonUICallback': zaction.ProcTypeDef(isMaster=True, procCategory='UI', properties=[zaction.ProcPropertyTypeDef('callbackKey', 'S', userDataType=None, isPrivate=True)]),
 'actionProcTypes.PlayEntityAudio': zaction.ProcTypeDef(isMaster=True, procCategory='Audio', properties=[zaction.ProcPropertyTypeDef('audioName', 'S', userDataType=None, isPrivate=True, displayName='Audio Name'), zaction.ProcPropertyTypeDef('mls', 'B', userDataType=None, isPrivate=True, displayName='MLS')]),
 'actionProcTypes.PlayTutorialVoiceover': zaction.ProcTypeDef(isMaster=True, procCategory='Audio', properties=[zaction.ProcPropertyTypeDef('messageKey', 'S', userDataType=None, isPrivate=True, displayName='MLS Message Key')]),
 'actionProcTypes.PushCameraWithTransition': zaction.ProcTypeDef(isMaster=True, procCategory='Camera', properties=[zaction.ProcPropertyTypeDef('cameraName', 'S', userDataType=None, isPrivate=True, displayName='Camera Class Name'),
                                              zaction.ProcPropertyTypeDef('behaviorNames', 'S', userDataType=None, isPrivate=True, displayName='Behavior Class Names (comma separ.)'),
                                              zaction.ProcPropertyTypeDef('transitionSeconds', 'F', userDataType=None, isPrivate=True, displayName='Transition Seconds'),
                                              zaction.ProcPropertyTypeDef('startHeight', 'F', userDataType=None, isPrivate=True, displayName='Start Height From Floor')]),
 'actionProcTypes.PopCameraWithTransition': zaction.ProcTypeDef(isMaster=True, procCategory='Camera', properties=[zaction.ProcPropertyTypeDef('transitionSeconds', 'F', userDataType=None, isPrivate=True, displayName='Transition Seconds'), zaction.ProcPropertyTypeDef('retainYaw', 'B', userDataType=None, isPrivate=True, displayName='Retain yaw between cameras'), zaction.ProcPropertyTypeDef('retainPitch', 'B', userDataType=None, isPrivate=True, displayName='Retain pitch between cameras')])}

