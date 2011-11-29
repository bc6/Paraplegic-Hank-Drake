import collections
import copy

class BaseComponentView(object):
    __guid__ = 'cef.BaseComponentView'
    RECIPE = 1
    SPAWN_ONLY = 2
    RUNTIME = 4
    ALL_STATIC_RECIPE = RECIPE
    ALL_STATIC = SPAWN_ONLY | RECIPE
    ALL_SPAWN = SPAWN_ONLY
    __COMPONENT_CLASS_BY_ID__ = {}
    __SHOULD_SPAWN__ = {}
    __DESCRIPTION__ = 'No description for component'

    @classmethod
    def RegisterComponent(cls, componentClass):
        if componentClass.__COMPONENT_ID__ in BaseComponentView.__COMPONENT_CLASS_BY_ID__ and componentClass.__guid__ != BaseComponentView.__COMPONENT_CLASS_BY_ID__[componentClass.__COMPONENT_ID__].__guid__:
            raise RuntimeError('Two componentViews are trying to register the same componentID:', BaseComponentView.__COMPONENT_CLASS_BY_ID__[componentClass.__COMPONENT_ID__], 'and', componentClass, BaseComponentView.__COMPONENT_CLASS_BY_ID__[componentClass.__COMPONENT_ID__] is componentClass)
        BaseComponentView.__COMPONENT_CLASS_BY_ID__[componentClass.__COMPONENT_ID__] = componentClass
        cls.__INPUT_DATATYPES__ = collections.OrderedDict()
        cls.__INPUT_GROUP__ = {}
        cls.__INPUT_CALLBACKS__ = {}
        cls.__INPUT_KEYWORDS__ = {}
        cls.__INPUT_DISPLAY_NAMES__ = {}
        cls.__INPUT_NEEDS_TRANSLATED__ = set()
        cls.__INIT_DEFAULTS__ = {}



    @staticmethod
    def RegisterCustomDisplay(componentID, customDisplayType):
        componentView = BaseComponentView.GetComponentViewByID(componentID)
        componentView.__COMPONENT_CUSTOM_DISPLAY__ = customDisplayType


    __COMPONENT_ID__ = const.cef.INVALID_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'INVALID NAME'
    __COMPONENT_CODE_NAME__ = 'INVALID'
    __COMPONENT_CUSTOM_DISPLAY__ = None
    __COMPONENT_DEPENDENCIES__ = []

    @classmethod
    def SetupInputs(cls):
        raise NotImplementedError('If you explicitly have no inputs, implement this function, but only call cls.RegisterComponent(cls)')



    @classmethod
    def _AddInput(cls, initValueNameTuple, defaultTuple, group, datatypeID, callback = None, needsTranslation = False, displayName = None, **kw):
        if isinstance(initValueNameTuple, str):
            initValueNameTuple = (initValueNameTuple,)
            defaultTuple = (defaultTuple,)
        if datatypeID == const.cef.COMPONENTDATA_INVALID_TYPE:
            raise ValueError('Invalid Type is not meant to be used as an input type.')
        if group & cls.ALL_STATIC and datatypeID == const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE:
            raise ValueError('Non-Primitive Type cannot be a static input (must fit in a db row).')
        cls.__INPUT_DATATYPES__[initValueNameTuple] = datatypeID
        cls.__INPUT_GROUP__[initValueNameTuple] = group
        cls.__INPUT_DISPLAY_NAMES__[initValueNameTuple] = displayName
        if callback is not None:
            cls.__INPUT_CALLBACKS__[initValueNameTuple] = callback
        cls.__INPUT_KEYWORDS__[initValueNameTuple] = kw
        if needsTranslation:
            cls.__INPUT_NEEDS_TRANSLATED__.update(initValueNameTuple)
        cls.__INIT_DEFAULTS__.update(zip(initValueNameTuple, defaultTuple))



    @classmethod
    def GetInputs(cls, groupFilter = ALL_STATIC):
        return [ initValueNameTuple for initValueNameTuple in cls.__INPUT_DATATYPES__.iterkeys() if cls.__INPUT_GROUP__[initValueNameTuple] & groupFilter ]



    @classmethod
    def GetDependencies(cls):
        return set(cls.__COMPONENT_DEPENDENCIES__)



    @classmethod
    def GetDataTypeID(cls, initValueNameTuple):
        return cls.__INPUT_DATATYPES__.get(initValueNameTuple, const.cef.COMPONENTDATA_INVALID_TYPE)



    @classmethod
    def GetInputGroup(cls, initValueNameTuple):
        return cls.__INPUT_GROUP__.get(initValueNameTuple)



    @classmethod
    def GetCallback(cls, initValueNameTuple):
        return cls.__INPUT_CALLBACKS__.get(initValueNameTuple)



    @classmethod
    def GetKeywords(cls, initValueNameTuple):
        return cls.__INPUT_KEYWORDS__.get(initValueNameTuple, {})



    @classmethod
    def GetNeedsTranslation(cls, initValueName):
        return initValueName in cls.__INPUT_NEEDS_TRANSLATED__



    @classmethod
    def GetDisplayName(cls, initValueNameTuple):
        return cls.__INPUT_DISPLAY_NAMES__.get(initValueNameTuple)



    @classmethod
    def GetDefault(cls, initValueName):
        return cls.__INIT_DEFAULTS__[initValueName]



    @staticmethod
    def GetComponentViewByID(componentID):
        return BaseComponentView.__COMPONENT_CLASS_BY_ID__.get(componentID)



    @staticmethod
    def GetComponentLookupDict():
        return copy.deepcopy(BaseComponentView.__COMPONENT_CLASS_BY_ID__)



    @staticmethod
    def GetComponentsWithDatatype(targetDatatypeID):
        searchResults = {}
        for (componentID, componentView,) in BaseComponentView.__COMPONENT_CLASS_BY_ID__.iteritems():
            for (initValueNameTuple, curDatatypeID,) in componentView.__INPUT_DATATYPES__.iteritems():
                if curDatatypeID == targetDatatypeID:
                    if componentID not in searchResults:
                        searchResults[componentID] = []
                    searchResults[componentID].append(initValueNameTuple)


        return searchResults



    @staticmethod
    def GetDefaultRecipe(componentID, groupFilter = RECIPE):
        componentView = BaseComponentView.GetComponentViewByID(componentID)
        if componentView is None:
            return {}
        filteredInputTuples = componentView.GetInputs(groupFilter=groupFilter)
        filteredInputNames = set()
        for initValueNameTuple in filteredInputTuples:
            filteredInputNames.update(initValueNameTuple)

        return {initialValueName:defaultValue for (initialValueName, defaultValue,) in componentView.__INIT_DEFAULTS__.iteritems() if initialValueName in filteredInputNames}



    @classmethod
    def GetComponentCodeName(cls):
        return cls.__COMPONENT_CODE_NAME__



    @classmethod
    def ValidateComponent(cls, result, recipeID, recipeDict):
        return True




