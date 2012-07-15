#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/actionObjectComponentView.py
import cef
import zactionobject

class ActionObjectComponentView(cef.BaseComponentView):
    __guid__ = 'cef.ActionObjectComponentView'
    __COMPONENT_ID__ = const.cef.ACTION_OBJECT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Action Object'
    __COMPONENT_CODE_NAME__ = 'actionObject'
    OCCUPANTS = 'actionStationOccupants'
    ACTIONOBJECT_ID = 'actionObjectUID'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.OCCUPANTS, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Action Station Occupants')
        cls._AddInput(cls.ACTIONOBJECT_ID, 0, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, cls.GetActionObjectsEnum, displayName='Action Object ID')

    @staticmethod
    def GetActionObjectsEnum():
        rows = zactionobject.ActionObject.GetMyRows(_getDeleted=False)
        return [ (actionObject.actionObjectName, actionObject.actionObjectID, '') for actionObject in rows ]

    @classmethod
    def ValidateComponent(cls, result, recipeID, recipeDict):
        dropDownEntries = cls.GetActionObjectsEnum()
        validIDs = [ entry[1] for entry in dropDownEntries ]
        actionObjectID = recipeDict[cls.__COMPONENT_ID__][cls.ACTIONOBJECT_ID]
        if actionObjectID not in validIDs:
            result.AddMessage('Invalid actionObjectID: %s' % actionObjectID)


ActionObjectComponentView.SetupInputs()