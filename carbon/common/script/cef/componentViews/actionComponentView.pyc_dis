#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/actionComponentView.py
import cef
import zaction

class ActionComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ActionComponentView'
    __COMPONENT_ID__ = const.cef.ACTION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'ActionTree'
    __COMPONENT_CODE_NAME__ = 'action'
    DEFAULT_ACTION_ID = const.zaction.ACTIONTREE_RECIPE_DEFAULT_ACTION_NAME

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.DEFAULT_ACTION_ID, None, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetActionList, displayName='Default Action')

    @staticmethod
    def _GetActionList(*args):
        actionList = zaction.Tree.GetActionNameIDMappingList()
        validList = [ (action[0], action[1], '') for action in actionList ]
        return validList


ActionComponentView.SetupInputs()