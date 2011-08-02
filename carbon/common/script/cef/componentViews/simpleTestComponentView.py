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
        cls._AddInput(cls.TEST_GRAPHIC_ID, -1, cls.MANDATORY, const.cef.COMPONENTDATA_GRAPHIC_ID_TYPE)
        cls._AddInput(cls.TEST_ID, -1, cls.OPTIONAL, const.cef.COMPONENTDATA_ID_TYPE)
        cls._AddInput(cls.TEST_STR, '', cls.OPTIONAL, const.cef.COMPONENTDATA_STRING_TYPE)
        cls._AddInput(cls.TEST_INT, 0, cls.OPTIONAL, const.cef.COMPONENTDATA_INT_TYPE)
        cls._AddInput(cls.TEST_FLOAT, 0.0, cls.OPTIONAL, const.cef.COMPONENTDATA_FLOAT_TYPE)
        cls._AddInput(cls.TEST_BOOL, 0, cls.OPTIONAL, const.cef.COMPONENTDATA_BOOL_TYPE)
        cls._AddInput(cls.TEST_VECTOR, '(0.0,0.0,0.0)', cls.OPTIONAL, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE)
        cls._AddInput(cls.TEST_COLOR_RGBA, (1.0, 1.0, 1.0, 1.0), cls.OPTIONAL, const.cef.COMPONENTDATA_COLOR_TYPE)
        cls._AddInput(cls.TEST_COLOR_RGB, (1.0, 1.0, 1.0), cls.OPTIONAL, const.cef.COMPONENTDATA_COLOR_TYPE)



SimpleTestComponentView.SetupInputs()

