#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/cef/componentViews/spawnLocationComponentView.py
import cef

class SpawnLocationComponentView(cef.BaseComponentView):
    __guid__ = 'cef.SpawnLocationComponentView'
    __COMPONENT_ID__ = const.cef.SPAWN_LOCATION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Spawn Location'
    __COMPONENT_CODE_NAME__ = 'spawnLocation'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'Marks the spawn as a spawn location for the CQs.  Different types indicate different reasons to spawn there.'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput('spawnLocationType', 0, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetEnum, displayName='Spawn Location Type')
        cls._AddInput('cameraYaw', 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Camera Yaw')
        cls._AddInput('cameraPitch', 1.93, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Camera Pitch')
        cls._AddInput('cameraZoom', 2.9, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Camera Zoom')

    @classmethod
    def _GetEnum(*args):
        enum = []
        for locationType, name in const.cef.CQ_SPAWN_LOCATION_TYPE_NAMES.iteritems():
            enum.append((name, locationType, name))

        return enum


SpawnLocationComponentView.SetupInputs()