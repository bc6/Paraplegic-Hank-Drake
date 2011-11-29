import cef

class AimingComponentView(cef.BaseComponentView):
    __guid__ = 'cef.AimingComponentView'
    __COMPONENT_ID__ = const.cef.AIMING_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Aiming'
    __COMPONENT_CODE_NAME__ = 'aiming'
    __COMPONENT_DEPENDENCIES__ = [const.cef.POSITION_COMPONENT_ID]
    ENTITY_TYPE = 'entityType'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.ENTITY_TYPE, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Entity Type')



AimingComponentView.SetupInputs()

