import cef

class ContextMenuComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ContextMenuComponentView'
    __COMPONENT_ID__ = const.cef.CONTEXT_MENU_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Context Menu'
    __COMPONENT_CODE_NAME__ = 'contextMenu'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)



ContextMenuComponentView.SetupInputs()

