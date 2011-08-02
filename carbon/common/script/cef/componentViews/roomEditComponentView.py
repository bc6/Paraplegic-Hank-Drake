import cef

class RoomEditComponentView(cef.BaseComponentView):
    __guid__ = 'cef.RoomEditComponentView'
    __COMPONENT_ID__ = const.cef.ROOM_EDIT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Room Edit'
    __COMPONENT_CODE_NAME__ = 'roomEdit'
    ITEM_ID = 'itemID'
    TYPE_ID = 'typeID'
    WORLDSPACE_ID = 'worldspaceID'
    POS = 'pos'
    ROT = 'rot'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.ITEM_ID, -1, cls.MANDATORY, const.cef.COMPONENTDATA_ID_TYPE)
        cls._AddInput(cls.TYPE_ID, -1, cls.MANDATORY, const.cef.COMPONENTDATA_ID_TYPE)
        cls._AddInput(cls.WORLDSPACE_ID, -1, cls.MANDATORY, const.cef.COMPONENTDATA_ID_TYPE)
        cls._AddInput(cls.POS, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)
        cls._AddInput(cls.ROT, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)



RoomEditComponentView.SetupInputs()

