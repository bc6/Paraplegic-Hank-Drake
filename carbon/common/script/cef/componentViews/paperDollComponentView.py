import cef

class PaperDollComponentView(cef.BaseComponentView):
    __guid__ = 'cef.PaperDollComponentView'
    __COMPONENT_ID__ = const.cef.PAPER_DOLL_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'PaperDoll'
    __COMPONENT_CODE_NAME__ = 'paperdoll'
    GENDER = 'gender'
    DNA = 'dna'
    TYPE_ID = 'typeID'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GENDER, None, cls.OPTIONAL, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetGenderTypesEnum)
        cls._AddInput(cls.DNA, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE)
        cls._AddInput(cls.TYPE_ID, 0, cls.RUNTIME, const.cef.COMPONENTDATA_ID_TYPE)



    @staticmethod
    def _GetGenderTypesEnum(*args):
        genderList = []
        genderList.append(('Female', const.FEMALE, 'Female'))
        genderList.append(('Male', const.MALE, 'Male'))
        return genderList



PaperDollComponentView.SetupInputs()

