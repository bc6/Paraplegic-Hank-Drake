import cef

class MinigameAIView(cef.BaseComponentView):
    __guid__ = 'cef.MinigameAIView'
    __COMPONENT_ID__ = const.cef.MINIGAME_AI_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Minigame AI'
    __COMPONENT_CODE_NAME__ = 'minigameAI'
    GAME_TYPE = 'gameType'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GAME_TYPE, -1, cls.RECIPE, const.cef.COMPONENTDATA_ID_TYPE, displayName='Game Type')



MinigameAIView.SetupInputs()

