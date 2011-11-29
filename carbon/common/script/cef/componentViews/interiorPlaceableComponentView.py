import cef
import blue

class InteriorPlaceableComponentView(cef.BaseComponentView):
    __guid__ = 'cef.InteriorPlaceableComponentView'
    __COMPONENT_ID__ = const.cef.INTERIOR_PLACEABLE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'InteriorPlaceable'
    __COMPONENT_CODE_NAME__ = 'interiorPlaceable'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'Contains the graphicID and handles the loading for placeable objects'
    GRAPHIC_ID = 'graphicID'
    MIN_SPEC_MATERIAL_PATH = 'minSpecOverideMetaMaterialPath'
    OVERRIDE_MATERIAL_PATH = 'overrideMetaMaterialPath'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GRAPHIC_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_GRAPHIC_ID_TYPE, displayName='Graphic ID')
        cls._AddInput(cls.MIN_SPEC_MATERIAL_PATH, None, cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='MinSpec Material Path', fileTypes='Red Files (*.red)|*.red')
        cls._AddInput(cls.OVERRIDE_MATERIAL_PATH, None, cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Override Material Path', fileTypes='Red Files (*.red)|*.red')
        cls._AddInput('probeOffsetX', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='SH Probe Offset X')
        cls._AddInput('probeOffsetY', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='SH Probe Offset Y')
        cls._AddInput('probeOffsetZ', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='SH Probe Offset Z')
        cls._AddInput('depthOffset', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Transparency Depth Offset')
        cls._AddInput('scale', '(1.0,1.0,1.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Scale')



    @classmethod
    def ValidateComponent(cls, result, recipeID, recipeDict):
        resFile = blue.ResFile()
        materialPath = recipeDict[cls.__COMPONENT_ID__][cls.MIN_SPEC_MATERIAL_PATH]
        if materialPath is not None and not resFile.FileExists(materialPath):
            result.AddMessage('MisSpec material path is invalid: "%s"' % materialPath)
        overridePath = recipeDict[cls.__COMPONENT_ID__][cls.OVERRIDE_MATERIAL_PATH]
        if overridePath is not None and not resFile.FileExists(overridePath):
            result.AddMessage('Override material path is invalid: "%s"' % overridePath)
        scale = recipeDict[cls.__COMPONENT_ID__]['scale']
        if scale != '(1.0,1.0,1.0)' and const.cef.COLLISION_MESH_COMPONENT_ID in recipeDict:
            result.AddMessage('Cannot scale a placeable with collision')



InteriorPlaceableComponentView.SetupInputs()

