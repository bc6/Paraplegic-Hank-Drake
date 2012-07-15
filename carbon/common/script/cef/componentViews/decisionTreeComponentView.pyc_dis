#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/decisionTreeComponentView.py
import cef
import ai

class DecisionTreeComponentView(cef.BaseComponentView):
    __guid__ = 'cef.DecisionTreeComponentView'
    __COMPONENT_ID__ = const.cef.DECISION_TREE_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Decision Tree'
    __COMPONENT_CODE_NAME__ = 'decision'
    DECISION_TREE_CLIENT_ROOT_ID = 'DecisionTreeClientRoot'
    DECISION_TREE_SERVER_ROOT_ID = 'DecisionTreeServerRoot'
    DECISION_TREE_HATE_ROOT_ID = 'HateTreeServerRoot'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.DECISION_TREE_CLIENT_ROOT_ID, None, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, cls._GetDecisionTreeList)
        cls._AddInput(cls.DECISION_TREE_SERVER_ROOT_ID, None, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, cls._GetDecisionTreeList)
        cls._AddInput(cls.DECISION_TREE_HATE_ROOT_ID, None, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, cls._GetDecisionTreeList)

    @staticmethod
    def _GetDecisionTreeList():
        decisionTreeRows = ai.DecisionLink.GetAllChildTreesByParentID(0)
        validList = [ (decisionTreeRow.treeNodeName, decisionTreeRow.treeNodeID, '') for decisionTreeRow in decisionTreeRows ]
        return validList


DecisionTreeComponentView.SetupInputs()