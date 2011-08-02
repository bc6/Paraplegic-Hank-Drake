import cef

class ProximityOpenTutorialView(cef.BaseComponentView):
    __guid__ = 'cef.ProximityOpenTutorialView'
    __COMPONENT_ID__ = const.cef.PROXIMITY_OPEN_TUTORIAL_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Proximity Open Tutorial'
    __COMPONENT_CODE_NAME__ = 'proximityOpenTutorial'
    TUTORIAL_ID = 'tutorialID'
    RADIUS = 'radius'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.TUTORIAL_ID, -1, cls.MANDATORY, const.cef.COMPONENTDATA_ID_TYPE)
        cls._AddInput(cls.RADIUS, 0.0, cls.MANDATORY, const.cef.COMPONENTDATA_FLOAT_TYPE)



ProximityOpenTutorialView.SetupInputs()

