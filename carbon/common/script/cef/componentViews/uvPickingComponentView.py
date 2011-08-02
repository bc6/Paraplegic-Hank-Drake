import cef

class UVPickingComponentView(cef.BaseComponentView):
    __guid__ = 'cef.UVPickingComponentView'
    __COMPONENT_ID__ = const.cef.UV_PICKING_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'UV Picking'
    __COMPONENT_CODE_NAME__ = 'uvPicking'
    AREA_NAME = 'areaName'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.AREA_NAME, '', cls.MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE)



UVPickingComponentView.SetupInputs()

