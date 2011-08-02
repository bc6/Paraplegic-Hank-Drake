import cef

class DecisionTreeComponentView(cef.BaseComponentView):
    __guid__ = 'cef.DecisionTreeComponentView'
    __COMPONENT_ID__ = const.cef.DECISION_TREE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Decision Tree'
    __COMPONENT_CODE_NAME__ = 'decision'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)



DecisionTreeComponentView.SetupInputs()

