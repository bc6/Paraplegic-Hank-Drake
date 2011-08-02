import svc
CONTROL_PARAMETER_TRACK_NAME_PREFIX = 'CP_'
AUDIO_EVENT_TRACK_NAME = 'Sound'
FOOTSTEP_SOUNDID = 10009

class EveAnimationClient(svc.animationClient):
    __guid__ = 'svc.eveAnimationClient'
    __replaceservice__ = 'animationClient'

    def __init__(self):
        svc.animationClient.__init__(self)



    def _ProcessMorphemeDiscreteEvent(self, animationController, animRef, trackID, eventUserData, trackUserData):
        controllerTracks = animationController.GetEventTrackIDs()
        trackName = animationController.GetEventTrackName(trackID)
        if trackName == AUDIO_EVENT_TRACK_NAME:
            entity = self.networkToController.get(animRef).entityRef
            if eventUserData == FOOTSTEP_SOUNDID:
                sm.GetService('audio').PlayFootfallForEntity(entity)
            else:
                sm.GetService('audio').SendEntityEventBySoundID(entity, eventUserData)
        elif trackName.startswith(CONTROL_PARAMETER_TRACK_NAME_PREFIX) and animationController.GetControlParameter(trackName[3:]) is not None:
            animationController.SetControlParameter(trackName[3:], eventUserData)



    def _AnimationSetupHook(self, entity, component):
        if component.controller is not None:
            self.RegisterAnimationController(component.controller, audioCueFile=None)




