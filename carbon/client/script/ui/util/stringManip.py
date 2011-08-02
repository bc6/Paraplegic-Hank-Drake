import uiutil
import re
import uiconst

def PrepareArgs(args):
    dest = {}
    arg = args.split('&')
    for i in arg:
        kv = i.split('=', 1)
        if len(kv) == 2:
            s = kv[1]
            if dest.has_key(kv[0]):
                if type(dest[kv[0]]) != type([]):
                    dest[kv[0]] = [dest[kv[0]]]
                dest[kv[0]].append(s)
            else:
                dest[kv[0]] = s
        else:
            dest[i] = ''

    return dest



def Zip(*parts):
    return '\t'.join(parts)



def Unzip(s):
    if '\t' in s:
        return s.split('\t')
    else:
        return [ each.replace('\\|', '|') for each in s.split('||') ]



def StripTags(s, ignoredTags = [], stripOnly = []):
    if not s:
        return s
    else:
        regex = '|'.join([ '</?%s>|<%s *=.*?>' % (tag, tag) for tag in stripOnly or ignoredTags ])
        if stripOnly:
            return ''.join(re.split(regex, s))
        if ignoredTags:
            for matchingTag in [ tag for tag in re.findall('<.*?>', s) if tag not in re.findall(regex, s) ]:
                s = s.replace(matchingTag, '')

            return s
        return ''.join(re.split('<.*?>', s))



def GetLevel(lvl):
    return ['-',
     'I',
     'II',
     'III',
     'IV',
     'V'][min(5, lvl)]



def IntToRoman(value):
    if value > 3999 or value < 1:
        return 'N/A'
    roman = ''
    for (r, v, s,) in (('M', 1000, (('CM', 900), ('D', 500), ('CD', 400))),
     ('C', 100, (('XC', 90), ('L', 50), ('XL', 40))),
     ('X', 10, (('IX', 9), ('V', 5), ('IV', 4))),
     ('I', 1, ())):
        while value > v - 1:
            roman += r
            value -= v

        for (rs, vs,) in s:
            if value > vs - 1:
                roman += rs
                value -= vs


    return roman



def RomanToInt(roman):
    d = {'I': 1,
     'V': 5,
     'X': 10,
     'L': 50,
     'C': 100,
     'D': 500,
     'M': 1000}
    nums = []
    for r in roman.upper():
        i = d.get(r, 0)
        if not nums:
            nums.append(i)
            continue
        if i > nums[-1]:
            nums[-1] = -nums[-1]
        nums.append(i)

    return sum(nums)



def UpperCase(string):
    if session.languageID == 'RU':
        return string
    if string is None:
        return ''
    string = string.upper()
    return string



def FindTextBoundaries(text, regexObject = None):
    import uiconst
    regexObject = regexObject or uiconst.LINE_BREAK_BOUNDARY_REGEX
    return [ token for token in regexObject.split(text) if token ]


exports = uiutil.AutoExports('uiutil', locals())

