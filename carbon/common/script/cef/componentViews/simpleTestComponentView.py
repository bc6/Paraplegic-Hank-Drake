import cef

class SimpleTestComponentView(cef.BaseComponentView):
    __guid__ = 'cef.SimpleTestComponentView'
    __COMPONENT_ID__ = const.cef.SIMPLE_TEST_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Simple Test Component'
    __COMPONENT_CODE_NAME__ = 'simpleTestComponent'
    TEST_GRAPHIC_ID = 'graphicID'
    TEST_ID = 'testID'
    TEST_STR = 'testStr'
    TEST_INT = 'testInt'
    TEST_FLOAT = 'testFloat'
    TEST_BOOL = 'testBool'
    TEST_VECTOR = 'testAwkward'
    TEST_COLOR_RGBA = ('testRed', 'testBlue', 'testGreen', 'testAlpha')
    TEST_COLOR_RGB = ('testR', 'testB', 'testG')

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.TEST_GRAPHIC_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_GRAPHIC_ID_TYPE, displayName='Test Graphic ID')
        cls._AddInput(cls.TEST_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_ID_TYPE, displayName='Test ID')
        cls._AddInput(cls.TEST_STR, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Test Str')
        cls._AddInput(cls.TEST_INT, 0, cls.RECIPE, const.cef.COMPONENTDATA_INT_TYPE, displayName='Test Int')
        cls._AddInput(cls.TEST_FLOAT, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Test Float')
        cls._AddInput(cls.TEST_BOOL, 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Test Bool')
        cls._AddInput(cls.TEST_VECTOR, '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Test Vector')
        cls._AddInput(cls.TEST_COLOR_RGBA, (1.0, 1.0, 1.0, 1.0), cls.RECIPE, const.cef.COMPONENTDATA_COLOR_TYPE, displayName='Test Color RGBA')
        cls._AddInput(cls.TEST_COLOR_RGB, (1.0, 1.0, 1.0), cls.RECIPE, const.cef.COMPONENTDATA_COLOR_TYPE, displayName='Test Color RGB')



SimpleTestComponentView.SetupInputs()

