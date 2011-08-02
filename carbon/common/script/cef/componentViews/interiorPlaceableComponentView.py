import cef

class InteriorPlaceableComponentView(cef.BaseComponentView):
    __guid__ = 'cef.InteriorPlaceableComponentView'
    __COMPONENT_ID__ = const.cef.INTERIOR_PLACEABLE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'InteriorPlaceable'
    __COMPONENT_CODE_NAME__ = 'interiorPlaceable'
    GRAPHIC_ID = 'graphicID'
    MIN_SPEC_MATERIAL_PATH = 'minSpecOverideMetaMaterialPath'
    OVERRIDE_MATERIAL_PATH = 'overrideMetaMaterialPath'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GRAPHIC_ID, -1, cls.OPTIONAL, const.cef.COMPONENTDATA_GRAPHIC_ID_TYPE, displayName='Graphic ID')
        cls._AddInput(cls.MIN_SPEC_MATERIAL_PATH, '', cls.OPTIONAL, const.cef.COMPONENTDATA_STRING_TYPE, displayName='MinSpec Material Path')
        cls._AddInput(cls.OVERRIDE_MATERIAL_PATH, '', cls.OPTIONAL, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Override Material Path')



InteriorPlaceableComponentView.SetupInputs()

