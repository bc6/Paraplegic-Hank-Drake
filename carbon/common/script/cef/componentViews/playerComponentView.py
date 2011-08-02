import cef

class PlayerComponentView(cef.BaseComponentView):
    __guid__ = 'cef.PlayerComponentView'
    __COMPONENT_ID__ = const.cef.PLAYER_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Player'
    __COMPONENT_CODE_NAME__ = 'player'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)



PlayerComponentView.SetupInputs()

