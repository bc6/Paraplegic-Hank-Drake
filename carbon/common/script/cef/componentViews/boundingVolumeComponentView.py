import cef

class BoundingVolumeComponentView(cef.BaseComponentView):
    __guid__ = 'cef.BoundingVolumeComponentView'
    __COMPONENT_ID__ = const.cef.BOUNDING_VOLUME_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'BoundingVolume'
    __COMPONENT_CODE_NAME__ = 'boundingVolume'
    MIN = 'min'
    MAX = 'max'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.MIN, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Min')
        cls._AddInput(cls.MAX, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Max')



BoundingVolumeComponentView.SetupInputs()

