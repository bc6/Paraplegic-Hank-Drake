import cef

class ParticleObjectComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ParticleObjectComponentView'
    __COMPONENT_ID__ = const.cef.PARTICLE_OBJECT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Particle Object'
    __COMPONENT_CODE_NAME__ = 'particleObject'
    RED_FILE = 'redFile'
    POSITION_OFFSET = 'positionOffset'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.RED_FILE, '', cls.MANDATORY, const.cef.COMPONENTDATA_STRING_TYPE)
        cls._AddInput(cls.POSITION_OFFSET, '(0.0,0.0,0.0)', cls.OPTIONAL, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE)



ParticleObjectComponentView.SetupInputs()

