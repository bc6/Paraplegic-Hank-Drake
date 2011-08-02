import cef

class MinigameConfigView(cef.BaseComponentView):
    __guid__ = 'cef.MinigameConfigView'
    __COMPONENT_ID__ = const.cef.MINIGAME_CONFIG_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Minigame Config'
    __COMPONENT_CODE_NAME__ = 'MinigameConfig'
    GAME_TYPE = 'gameType'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GAME_TYPE, -1, cls.MANDATORY, const.cef.COMPONENTDATA_ID_TYPE)



MinigameConfigView.SetupInputs()

