#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/cef/componentViews/proximityOpenTutorialView.py
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
        cls._AddInput(cls.TUTORIAL_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_ID_TYPE, displayName='Tutorial ID')
        cls._AddInput(cls.RADIUS, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Radius')


ProximityOpenTutorialView.SetupInputs()