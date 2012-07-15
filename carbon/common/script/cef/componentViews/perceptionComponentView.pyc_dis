#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/cef/componentViews/perceptionComponentView.py
import cef
import perception

class PerceptionComponentView(cef.BaseComponentView):
    __guid__ = 'cef.PerceptionComponentView'
    __COMPONENT_ID__ = const.cef.PERCEPTION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Perception'
    __COMPONENT_CODE_NAME__ = 'perception'
    __COMPONENT_DEPENDENCIES__ = [const.cef.POSITION_COMPONENT_ID]
    ENTITY_TYPE = const.perception.PERCEPTION_COMPONENT_ENTITY_TYPE
    SENSE_GROUP_ID = const.perception.PERCEPTION_COMPONENT_SENSE_GROUP
    FILTER_GROUP_ID = const.perception.PERCEPTION_COMPONENT_FILTER_GROUP
    DECAY_GROUP_ID = const.perception.PERCEPTION_COMPONENT_DECAY_GROUP
    SENSOR_BONE_NAME = const.perception.PERCEPTION_COMPONENT_SENSOR_BONENAME
    SENSOR_OFFSET = const.perception.PERCEPTION_COMPONENT_SENSOR_OFFSET
    DROP_STIMTYPE = const.perception.PERCEPTION_COMPONENT_DROP_STIMTYPE
    DROP_STIMRANGE = const.perception.PERCEPTION_COMPONENT_DROP_RANGE
    TAGS = const.perception.PERCEPTION_COMPONENT_TAGS
    CLIENTSERVER = const.perception.PERCEPTION_COMPONENT_CLIENTSERVER

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.ENTITY_TYPE, '', cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetEntityTypeEnum, displayName='Entity Type')
        cls._AddInput(cls.SENSE_GROUP_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetSenseGroupEnum, displayName='Sense Group ID')
        cls._AddInput(cls.FILTER_GROUP_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetFilterGroupEnum, displayName='Filter Group ID')
        cls._AddInput(cls.DECAY_GROUP_ID, -1, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetDecayGroupEnum, displayName='Decay Group ID')
        cls._AddInput(cls.SENSOR_BONE_NAME, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Sensor Bone Name')
        cls._AddInput(cls.SENSOR_OFFSET, '', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='Sensor Offset')
        cls._AddInput(cls.DROP_STIMTYPE, '', cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetStimTypeEnum, displayName='Drop Stim Type')
        cls._AddInput(cls.DROP_STIMRANGE, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Drop Stim Range')
        cls._AddInput(cls.TAGS, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE)
        cls._AddInput(cls.CLIENTSERVER, const.perception.PERCEPTION_CLIENTSERVER_FLAG_BOTH, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetClientServerTypeEnum)

    @staticmethod
    def _GetStimTypeEnum(*args):
        showList = [ (row.stimTypeName, row.stimTypeName, row.stimTypeName) for row in perception.StimType.GetMyRows(_getDeleted=False) ]
        return showList

    @staticmethod
    def _GetEntityTypeEnum(*args):
        showList = [ (entry, entry, entry) for entry in const.perception.PERCEPTION_ENTITY_TYPE_TO_ID.keys() ]
        return showList

    @staticmethod
    def _GetSenseGroupEnum(*args):
        validList = [('None', 0, 'None')]
        validList.extend([ (row.description, row.senseGroupID, row.description) for row in perception.SenseGroup.GetMyRows(_getDeleted=False) ])
        return validList

    @staticmethod
    def _GetFilterGroupEnum(*args):
        validList = [('None', 0, 'None')]
        validList.extend([ (row.description, row.filterGroupID, row.description) for row in perception.FilterGroup.GetMyRows(_getDeleted=False) ])
        return validList

    @staticmethod
    def _GetDecayGroupEnum(*args):
        validList = [('None', 0, 'None')]
        validList.extend([ (row.description, row.decayGroupID, row.description) for row in perception.DecayGroup.GetMyRows(_getDeleted=False) ])
        return validList

    @staticmethod
    def _GetClientServerTypeEnum(*args):
        showList = [ (item[1], item[0], item[1]) for item in const.perception.PERCEPTION_CLIENTSERVER_FLAGS.items() ]
        return showList


PerceptionComponentView.SetupInputs()