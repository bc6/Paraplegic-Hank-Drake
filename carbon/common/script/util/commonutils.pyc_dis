#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/commonutils.py
import util
import re
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


def StripTags(s, ignoredTags = [], stripOnly = []):
    if not s or not isinstance(s, basestring):
        return s
    regex = '|'.join([ '</%s>|<%s>|<%s .*?>|<%s *=.*?>' % (tag,
     tag,
     tag,
     tag) for tag in stripOnly or ignoredTags ])
    if stripOnly:
        return ''.join(re.split(regex, s))
    elif ignoredTags:
        for matchingTag in [ tag for tag in re.findall('<.*?>', s) if tag not in re.findall(regex, s) ]:
            s = s.replace(matchingTag, '')

        return s
    else:
        return ''.join(re.split('<.*?>', s))


exports = {'util.IsFullLogging': IsFullLogging,
 'util.Truncate': Truncate,
 'util.Clamp': Clamp,
 'util.GetAttrs': GetAttrs,
 'util.HasDialogueHyperlink': HasDialogueHyperlink,
 'uiutil.StripTags': StripTags}