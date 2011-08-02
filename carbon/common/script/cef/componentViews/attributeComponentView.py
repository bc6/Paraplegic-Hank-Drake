import cef

class AttributeComponentView(cef.BaseComponentView):
    __guid__ = 'cef.AttributeComponentView'
    __COMPONENT_ID__ = const.cef.ATTRIBUTE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Attribute'
    __COMPONENT_CODE_NAME__ = 'attribute'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)



AttributeComponentView.SetupInputs()

