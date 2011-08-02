import blue
import blue.win32
import ctypes
commdev = 0
mem = 0
args = blue.pyos.GetArg()
for arg in args:
    if arg.startswith('/audiodev'):
        commdev = 1
        break
    if arg == '/audiomem':
        mem = 1
        break

if commdev == 1:
    try:
        from _audio2_dev import *
        print 'Audio2 imported from _audio2_dev'
    except ImportError:
        print 'Import from _audio2_dev failed - fallback to _audio2'
        from _audio2 import *
elif mem:
    try:
        from _audio2_mem import *
        print 'Audio2 imported from _audio2_mem for memory tracking'
    except ImportError:
        print 'Import from _audio2_mem failed - fallback to _audio2'
        from _audio2 import *
else:
    from _audio2 import *

def __RegisterEnums(namespace):

    class enumWrapper(object):
        pass
    for enum in GetRegisteredEnums():
        namespace[enum] = enumWrapper()
        namespace[enum].values = {}
        for (enumValueName, value, docString,) in GetRegisteredEnumValues(enum):
            setattr(namespace[enum], enumValueName, value)
            namespace[enum].values[enumValueName] = (value, docString)




__RegisterEnums(globals())

def GetEnumValueName(enumName, value):
    if enumName in globals():
        enum = globals()[enumName]
        result = ''
        for (enumKeyName, (enumKeyValue, enumKeydocString,),) in enum.values.iteritems():
            if enumKeyValue == value:
                if result != '':
                    result += ' | '
                result += enumKeyName

        return result



def GetEnumValueNameAsBitMask(enumName, value):
    if enumName in globals():
        enum = globals()[enumName]
        result = ''
        for (enumKeyName, (enumKeyValue, enumKeydocString,),) in enum.values.iteritems():
            if enumKeyValue & value == enumKeyValue:
                if result != '':
                    result += ' | '
                result += enumKeyName

        return result


del commdev
del args
del mem

