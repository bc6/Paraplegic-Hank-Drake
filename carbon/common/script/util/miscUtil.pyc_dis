#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/miscUtil.py
import blue
exports = {}
__debugPrint = False

def DebugPrint(self, *args):
    if __debugPrint:
        final = ''
        for arg in args:
            final += str(arg)

        if len(final) > 1:
            print final
        else:
            print None


exports['miscUtil.DebugPrint'] = DebugPrint

def GetCommonResourcePath(path):
    return path


def GetCommonResource(path):
    resourceFile = blue.ResFile()
    path = GetCommonResourcePath(path)
    result = resourceFile.Open(path)
    if result:
        return resourceFile
    else:
        return None


def CommonResourceExists(path):
    resourceFile = blue.ResFile()
    path = GetCommonResourcePath(path)
    return resourceFile.FileExists(path)


def IsInstance_BlueType(obj, name):
    return hasattr(obj, '__bluetype__') and obj.__bluetype__.find(name) >= 0


def Flatten(l, ltypes = (list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]

        i += 1

    return ltype(l)


exports['miscUtil.GetCommonResource'] = GetCommonResource
exports['miscUtil.GetCommonResourcePath'] = GetCommonResourcePath
exports['miscUtil.CommonResourceExists'] = CommonResourceExists
exports['miscUtil.IsInstance_BlueType'] = IsInstance_BlueType
exports['miscUtil.Flatten'] = Flatten