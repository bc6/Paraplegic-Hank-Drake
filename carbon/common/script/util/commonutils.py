import util
import blue
from service import ROLEMASK_ELEVATEDPLAYER

def IsFullLogging():
    return boot.role != 'client' or not blue.pyos.packaged or session.role & ROLEMASK_ELEVATEDPLAYER



class Object:
    __guid__ = 'util.Object'

    def __init__(self, **kw):
        self.__dict__.update(kw)



    def Get(self, key, defval = None):
        return self.__dict__.get(key, defval)



    def Set(self, key, value):
        self.__dict__[key] = value




def Truncate(number, numdec):
    if numdec >= 0:
        decshift = float(pow(10, numdec))
        return float(int(number * decshift)) / decshift
    else:
        return number



def Clamp(val, min_, max_):
    return min(max_, max(min_, val))



def GetAttrs(obj, *names):
    for name in names:
        obj = getattr(obj, name, None)
        if obj is None:
            return 

    return obj



def HasDialogueHyperlink(rawText):
    hasHyperlink = False
    openBracket = rawText.find('[')
    if openBracket > -1:
        nextCloseBracket = rawText.find(']', openBracket)
        if nextCloseBracket > -1:
            hasHyperlink = True
    return hasHyperlink


exports = {'util.IsFullLogging': IsFullLogging,
 'util.Truncate': Truncate,
 'util.Clamp': Clamp,
 'util.GetAttrs': GetAttrs,
 'util.HasDialogueHyperlink': HasDialogueHyperlink}

