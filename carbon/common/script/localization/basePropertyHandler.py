import localization

class BasePropertyHandler(object):
    __guid__ = 'localization.BasePropertyHandler'

    def __init__(self):
        if hasattr(self, 'PROPERTIES'):
            self._SetUpProperties()
        else:
            raise NotImplementedError, 'PropertyHandler cannot be instantiated.  You must create a PROPERTIES dictionary on your subclass.'



    def GetProperty(self, propertyName, identifierID, languageID):
        isUniversal = False
        method = self._propertyMethods.get((localization.CODE_UNIVERSAL, propertyName), None)
        if method is None:
            method = self._propertyMethods.get((languageID, propertyName), None)
        else:
            isUniversal = True
        if method is None:
            expectedMethodName = self._GeneratePropertyMethodName(propertyName, languageID)
            localization.LogError(str(self.__class__), " was asked for nonexisting property '", propertyName, "' method '", expectedMethodName, "' with language '", languageID, "'.")
            return 
        else:
            if isUniversal:
                return method(identifierID, languageID)
            return method(identifierID)



    def _SetUpProperties(self):
        self._propertyMethods = {}
        for aLanguage in self.PROPERTIES:
            propertyNames = self.PROPERTIES[aLanguage]
            for propertyName in propertyNames:
                methodName = self._GeneratePropertyMethodName(propertyName, aLanguage)
                isUniversal = True if aLanguage == localization.CODE_UNIVERSAL else False
                if not hasattr(self, methodName):
                    if isUniversal:
                        setattr(self, methodName, BasePropertyHandler._NotImplementedUniversalPropertyFactory(methodName))
                    else:
                        setattr(self, methodName, BasePropertyHandler._NotImplementedPropertyFactory(methodName))
                method = getattr(self, methodName)
                self._propertyMethods[(aLanguage, propertyName)] = method





    @staticmethod
    def _NotImplementedUniversalPropertyFactory(methodName):
        return lambda identifierID, languageID: BasePropertyHandler._NotImplementedProperty(methodName)



    @staticmethod
    def _NotImplementedPropertyFactory(methodName):
        return lambda identifierID: BasePropertyHandler._NotImplementedProperty(methodName)



    @staticmethod
    def _NotImplementedProperty(methodName):
        raise NotImplementedError, 'The property method (%s) is missing an implementation.' % methodName



    def _GeneratePropertyMethodName(self, propertyName, aLanguage):
        if aLanguage == localization.CODE_UNIVERSAL:
            newPropertyName = ''.join((propertyName[0].upper(), propertyName[1:]))
            methodName = ''.join(('_Get', newPropertyName))
        else:
            propertyNameParts = propertyName.split('.')
            for (index, each,) in enumerate(propertyNameParts):
                propertyNameParts[index] = ''.join((propertyNameParts[index][0].upper(), propertyNameParts[index][1:]))

            methodName = ''.join(('_Get', ''.join(propertyNameParts), aLanguage.replace('-', '_').upper()))
        return methodName




