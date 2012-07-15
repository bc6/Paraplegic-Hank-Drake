#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/graphics/tr2PyBindingHelpers.py
import util
import blue
import trinity
Tr2PyBindings = {'Tr2Vector4Parameter': 'Tr2PyBindingSentinelVector4',
 'Tr2Vector3Parameter': 'Tr2PyBindingSentinelVector3',
 'Tr2Vector2Parameter': 'Tr2PyBindingSentinelVector2',
 'Tr2FloatParameter': 'Tr2PyBindingSentinelFloat',
 'EveTransform': 'Tr2PyBindingSentinelMatrix4'}

def GetAllRootBindings(anObject):
    sourceList = list()
    destinationList = list()
    if hasattr(anObject, 'curveSets'):
        for aCurveSet in anObject.curveSets:
            if hasattr(aCurveSet, 'bindings'):
                for aBinding in aCurveSet.bindings:
                    if hasattr(aBinding.sourceObject, 'externalBind'):
                        sourceList.append(aBinding)
                    if hasattr(aBinding.destinationObject, 'externalBind'):
                        destinationList.append(aBinding)

    return (sourceList, destinationList)


def GetSourceRootBindings(anObject):
    sourceList, destinationList = GetAllRootBindings(anObject)
    return sourceList


def GetDestinationRootBindings(anObject):
    sourceList, destinationList = GetAllRootBindings(anObject)
    return destinationList


def GetAllBindings(anObject):
    sourceList, destinationList = GetAllRootBindings(anObject)
    if type(anObject) == list:
        for aMember in anObject:
            if hasattr(aMember, '__typename__'):
                aSourceList, aDestinationList = GetAllBindings(aMember)
                sourceList.extend(aSourceList)
                destinationList.extend(aDestinationList)

    elif hasattr(anObject, '__bluetype__') and anObject.__bluetype__ == 'blue.List':
        for aMember in anObject:
            if hasattr(aMember, '__typename__'):
                aSourceList, aDestinationList = GetAllBindings(aMember)
                sourceList.extend(aSourceList)
                destinationList.extend(aDestinationList)

    elif hasattr(anObject, '__members__'):
        for aMember in anObject.__members__:
            member = eval('anObject.' + aMember)
            if hasattr(member, '__typename__'):
                aSourceList, aDestinationList = GetAllBindings(member)
                sourceList.extend(aSourceList)
                destinationList.extend(aDestinationList)

    return (sourceList, destinationList)


def GetAllSourceBindings(anObject):
    sourceList, destinationList = GetAllBindings(anObject)
    return sourceList


def GetAllDestinationBindings(anObject):
    sourceList, destinationList = GetAllBindings(anObject)
    return destinationList


def GetTr2PyBindingFromTypeName(typename):
    if typename in Tr2PyBindings:
        return Tr2PyBindings[typename]


exports = util.AutoExports('trinity', locals())