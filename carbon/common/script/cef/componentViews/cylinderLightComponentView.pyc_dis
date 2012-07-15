#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/cylinderLightComponentView.py
import cef
DEFAULT_RADIUS = 1.0
DEFAULT_LENGTH = 1.0

class CylinderLightComponentView(cef.BaseComponentView, cef.LightComponentViewMixin):
    __guid__ = 'cef.CylinderLightComponentView'
    __COMPONENT_ID__ = const.cef.CYLINDER_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'CylinderLight'
    __COMPONENT_CODE_NAME__ = 'cylinderLight'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'Parameters for a trinity cylinder light'
    COLOR = ('red', 'green', 'blue')
    KELVINCOLOR = ('temperature', 'tint', 'whiteBalance')

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.COLOR, (1.0, 1.0, 1.0), cls.RECIPE, const.cef.COMPONENTDATA_COLOR_TYPE, displayName='Color')
        cls._AddInput('radius', DEFAULT_RADIUS, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Radius')
        cls._AddInput('length', DEFAULT_LENGTH, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Length')
        cls._AddInput('falloff', 30.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Falloff')
        cls._AddInput('sectorAngleOuter', 180.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Angle Outer')
        cls._AddInput('sectorAngleInner', 180.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Angle Inner')
        cls._AddInput('specularIntensity', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Specular Intensity')
        cls._AddInput('primaryLighting', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Primary Lighting')
        cls._AddInput('secondaryLighting', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Secondary Lighting')
        cls._AddInput('secondaryLightingMultiplier', 1.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Secondary Lighting Multiplier')
        cls._AddInput('projectedTexturePath', '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Projected Texture Path')
        cls._AddInput('isStatic', 1, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Is Static')
        cls._AddInput('useKelvinColor', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Kelvin Color')
        cls._AddInput(cls.KELVINCOLOR, (5500.0, 0.5, 2), cls.RECIPE, const.cef.COMPONENTDATA_KELVIN_COLOR_TYPE, displayName='Kelvin Color')
        cls._AddInput('performanceLevel', 0, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetPerformanceEnum, displayName='Performance Level', sortEnum=False)
        cls._AddInput('performanceLevel', 0, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetPerformanceEnum, displayName='Performance Level', sortEnum=False)
        cls._AddInput('useBoundingBox', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Bounding Box')
        cls._AddInput('bbPos', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Position')
        cls._AddInput('bbRot', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Rotation')
        cls._AddInput('bbScale', '(1.0,1.0,1.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Scale')


CylinderLightComponentView.SetupInputs()