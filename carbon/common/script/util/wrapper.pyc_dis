#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/wrapper.py


class Wrapper:
    __guid__ = 'util.Wrapper'
    __passbyvalue__ = 1

    def __init__(self, *args, **keywords):
        if args:
            self.__dict__['dict'] = args[0]
        else:
            self.__dict__['dict'] = keywords

    def __getattr__(self, attrName):
        if self.dict.has_key(attrName):
            return self.dict[attrName]
        raise AttributeError, attrName

    def __setattr__(self, attrName, attrValue):
        raise AttributeError, attrName