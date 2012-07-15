#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/benchmarkCameraComponentView.py
import cef

class BenchmarkCameraComponentView(cef.BaseComponentView):
    __guid__ = 'cef.BenchmarkCameraComponentView'
    __COMPONENT_ID__ = const.cef.BENCHMARK_CAMERA_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'BenchmarkCamera'
    __COMPONENT_CODE_NAME__ = 'benchmarkCamera'
    __SHOULD_SPAWN__ = {'client': False,
     'server': False}
    __DESCRIPTION__ = 'Marks the spot of a benchmark camera. This component has no use in client'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput('poi', '(0.0,0.0,0.0)', cls.SPAWN_ONLY, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='POI')


BenchmarkCameraComponentView.SetupInputs()