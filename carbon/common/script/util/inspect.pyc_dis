#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/inspect.py
import types

def IsClassMethod(func):
    if type(func) != types.MethodType:
        return False
    if type(func.im_self) is types.TypeType:
        return True
    return False


def IsStaticMethod(func):
    return type(func) == types.FunctionType


def IsNormalMethod(func):
    if type(func) != types.MethodType:
        return False
    if type(func.im_self) is not types.TypeType:
        return True
    return False


import util
exports = util.AutoExports('util', locals())