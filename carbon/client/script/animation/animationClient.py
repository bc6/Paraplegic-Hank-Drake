import service
import yaml
import animUtils
import blue
import GameWorld
import paperDoll
import animation
import safeThread
import collections
EVENT_TRACK_SOUND_LOOKUP_PATH = 'res:/Audio/animationEventTracks.yaml'

def OnMorphemeDiscreteEvents(animRef, *args):
    animationClient = sm.GetService('animationClient')
    for (trackID, eventUserData, trackUserData,) in args:
        animationController = animationClient.GetAnimationControllerFromNetwork(animRef)
        if animationController:
            animationClient._ProcessMorphemeDiscreteEvent(animationController, animRef, trackID, eventUserData, trackUserData)




class AnimationComponent:
    __guid__ = 'animation.AnimationComponent'

    def __init__(self):
        self.isClientPlayer = False
        self.updater = None
        self.controller = None
        self.poseState = None
        self.inThrow = False
        self.preThrowMode = None
        self.armTargetBone = {}
        self.armTargetBone['Left'] = None
        self.armTargetBone['Right'] = None
        self.attachments = {}
        self.poseObject = None
        self.idlePose = 'None'



    def AttachObject(self, obj, boneName, curveSet):
        if boneName in self.attachments:
            self.DetachObject(boneName)
        self.attachments[boneName] = {}
        self.attachments[boneName]['object'] = obj
        self.attachments[boneName]['curveSet'] = curveSet



    def DetachObject(self, boneName):
        del self.attachments[boneName]



    def GetAttachedCurveSet(self, boneName):
        return self.attachments[boneName]['curveSet']



    def GetAttachedObject(self, boneName):
        return self.attachments[boneName]['object']




class AnimationClient(service.Service, safeThread.SafeThread):
    __guid__ = 'svc.animationClient'
    __exportedcalls__ = {}
    __dependencies__ = ['paperDollClient']
    __notifyevents__ = []
    __componentTypes__ = ['animation']

    def __init__(self):
        service.Service.__init__(self)
        self.registeredControllers = {}
        self.registeredComponents = []
        self.networkToController = {}
        self.audioCueFiles = {}
        safeThread.SafeThread.init(self, 'svc.animationClient')
        self.safeThreadActive = False



    def Run(self, *etc):
        service.Service.Run(self)



    def _GetEntity(self, entid):
        raise StandardError('Not implemented')



    def GetEntityModel(self, entityID):
        raise StandardError('Not implemented')



    def _GetAnimationInfoService(self):
        raise StandardError('Not implemented')



    def _EntityNeedsToLineup(self, entity):
        raise StandardError('Not implemented')



    def _SetEntityMovement(self, ent, pos, rot, vel):
        raise StandardError('Not implemented')



    def _SwitchPlayerToDirectControlMode(self, force = False, remainingFacingAngle = 0.0):
        raise StandardError('Not implemented')



    def _ProcessMorphemeDiscreteEvent(self, animationController, animRef, eventUserData, trackUserData):
        raise StandardError('Not implemented')



    def _GetAudioCueFile(self, audioCueFilePath):
        if audioCueFilePath not in self.audioCueFiles:
            animEventFile = blue.ResFile()
            animEventFile.Open(audioCueFilePath)
            self.audioCueFiles[audioCueFilePath] = yaml.load(animEventFile)
            animEventFile.close()
        return self.audioCueFiles[audioCueFilePath]



    def GetAnimationControllerFromNetwork(self, networkReference):
        return self.networkToController.get(networkReference, None)



    def RegisterAnimationController(self, animationController, audioCueFile = EVENT_TRACK_SOUND_LOOKUP_PATH):
        if audioCueFile is not None:
            self.registeredControllers[animationController] = audioCueFile
            self._GetAudioCueFile(audioCueFile)
        self.networkToController[animationController.animationNetwork] = animationController
        animationController.animationNetwork.SetOnDiscreteEventCallback(OnMorphemeDiscreteEvents)



    def UnregisterAnimationController(self, animationController):
        if animationController in self.registeredControllers:
            del self.registeredControllers[animationController]
        if animationController.animationNetwork in self.networkToController:
            del self.networkToController[animationController.animationNetwork]



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        state = {'updater': component.updater,
         'controller': component.controller}
        return state



    def UnPackFromSceneTransfer(self, component, entity, state):
        return component



    def CreateComponent(self, name, state):
        component = AnimationComponent()
        component.updater = state.get('updater')
        component.controller = state.get('controller')
        component.poseState = state.get('poseState')
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        if entityID == session.charid:
            component.isClientPlayer = True
        if component.updater is None:
            component.updater = GameWorld.GWAnimation(None)
            component.updater.updateMode = 0



    def SetupComponent(self, entity, component):
        if component.updater.network is None:
            gender = self.paperDollClient.GetDBGenderToPaperDollGender(entity.paperdoll.gender)
            if gender == paperDoll.GENDER.MALE:
                component.updater.InitMorpheme(const.MALE_MORPHEME_PATH)
            else:
                component.updater.InitMorpheme(const.FEMALE_MORPHEME_PATH)
            if component.poseState is not None:
                component.updater.SetPoseByName(component.poseState)
        if component.controller is None:
            if component.isClientPlayer == True:
                component.controller = animation.PlayerAnimationController(component.updater.network)
            else:
                component.controller = animation.BipedAnimationController(component.updater.network)
        component.controller.entityRef = entity
        self.registeredComponents.append(component)
        self._AnimationSetupHook(entity, component)
        if self.safeThreadActive is False:
            self.LaunchSafeThreadLoop_BlueTime(const.ONE_TICK)
            self.safeThreadActive = True



    def _AnimationSetupHook(self, entity, component):
        pass



    def SafeThreadLoop(self, now):
        for component in self.registeredComponents:
            component.controller.Update()




    def UnRegisterComponent(self, entity, component):
        self.UnregisterAnimationController(component.controller)
        self.registeredComponents.remove(component)
        component.controller.entityRef = None
        component.controller = None
        component.updater = None



    def TearDownComponent(self, entity, component):
        pass



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Current LOD'] = component.controller.currentLOD
        report['Updated By'] = {0: 'GameWorld',
         1: 'Trinity'}[component.updater.updateMode]
        return report




