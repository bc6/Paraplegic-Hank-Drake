import cef

class ProximityComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ProximityComponentView'
    __COMPONENT_ID__ = const.cef.PROXIMITY_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Proximity'
    __COMPONENT_CODE_NAME__ = 'proximity'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)



ProximityComponentView.SetupInputs()

