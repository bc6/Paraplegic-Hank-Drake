import cef

class ActionObjectComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ActionObjectComponentView'
    __COMPONENT_ID__ = const.cef.ACTION_OBJECT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Action Object'
    __COMPONENT_CODE_NAME__ = 'actionObject'
    OCCUPANTS = 'actionStationOccupants'
    ACTIONOBJECT_ID = 'actionObjectUID'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.OCCUPANTS, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)
        cls._AddInput(cls.ACTIONOBJECT_ID, 0, cls.MANDATORY, const.cef.COMPONENTDATA_ACTIONOBJECT_ID_TYPE)



ActionObjectComponentView.SetupInputs()

