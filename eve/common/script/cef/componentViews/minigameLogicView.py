import cef

class MinigameLogicView(cef.BaseComponentView):
    __guid__ = 'cef.MinigameLogicView'
    __COMPONENT_ID__ = const.cef.MINIGAME_LOGIC_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Minigame Logic'
    __COMPONENT_CODE_NAME__ = 'minigameLogic'
    __COMPONENT_DEPENDENCIES__ = [const.cef.MINIGAME_AI_COMPONENT_ID, const.cef.MINIGAME_CONFIG_COMPONENT_ID]
    GAME_TYPE = 'gameType'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GAME_TYPE, -1, cls.RECIPE, const.cef.COMPONENTDATA_ID_TYPE, displayName='Game Type')



MinigameLogicView.SetupInputs()

