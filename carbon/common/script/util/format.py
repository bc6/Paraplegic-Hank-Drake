import log
import blue
import string
import math
import sys
import re
import const
SMALLDATETIME_MIN = 94432608000000000L
SMALLDATETIME_MAX = 150973632000000000L
__dateseptbl = string.maketrans('/-. ', '----')
DECIMAL = prefs.GetValue('decimal', '.')
DIGIT = prefs.GetValue('digit', ',')
ROMAN_NUMERAL_MAP = (('X', 1, 10),
 ('IX', 2, 9),
 ('V', 1, 5),
 ('IV', 2, 4),
 ('I', 1, 1))
romanNumeralPattern = re.compile("^                   # beginning of string\n(X{0,3})            # tens - 0-30 (0 to 3 X's),\n                    #\n(IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),\n                    #        or 5-8 (V, followed by 0 to 3 I's)\n$                   # end of string\n", re.VERBOSE)
urlHttpCheck = re.compile('\\Ahttp(s)?://', re.I)

def EscapeSQL(s, exactMatch = 0, min = 3):
    if not exactMatch:
        s = s.replace('%', '')
        s = s.replace('[', '[[]')
        s = s.replace('_', '[_]')
    return s



def EscapeAdHocSQL(s):
    s = s.replace("'", "''")
    s = s.replace('%', '')
    s = s.replace('[', '[[]')
    s = s.replace('_', '[_]')
    return s



def FmtTimeInterval(interval, breakAt = None, rounding = False):
    if interval < 10000L:
        return mls.UI_SHARED_FORMAT_SHORTAMOUNTTIME
    (year, month, wd, day, hour, min, sec, ms,) = blue.os.GetTimeParts(interval)
    year -= 1601
    month -= 1
    day -= 1
    items = []
    _s = ['', 's']
    if rounding:
        newInterval = interval
        if breakAt == 'sec':
            if ms >= 500:
                newInterval = interval / const.MSEC * const.MSEC + const.SEC
        elif breakAt == 'min':
            if sec >= 30:
                newInterval = interval / const.SEC * const.SEC + const.MIN
        elif breakAt == 'hour':
            if min >= 30:
                newInterval = interval / const.MIN * const.MIN + const.HOUR
        elif breakAt == 'day':
            if hour >= 12:
                newInterval = interval / const.HOUR * const.HOUR + const.DAY
        else:
            raise RuntimeError('Unsupported breakAt option for rounding=True')
        if newInterval != interval:
            return FmtTimeInterval(newInterval, breakAt)
    languageID = mls.GetLanguageID()
    while 1:
        if languageID == 'RU':
            if year:
                yearString = FindRussianYearString(year)
                items.append(str(year) + ' ' + yearString)
            if breakAt == 'year':
                break
            if month:
                items.append(str(month) + ' ' + mls.UI_GENERIC_MONTHVERYSHORT)
            if breakAt == 'month':
                break
            if day:
                items.append(str(day) + ' ' + mls.UI_GENERIC_DAYVERYSHORT)
            if breakAt == 'day':
                break
            if hour:
                items.append(str(hour) + ' ' + mls.UI_GENERIC_HOURVERYSHORT)
            if breakAt == 'hour':
                break
            if min:
                items.append(str(min) + ' ' + mls.UI_GENERIC_MINUTEVERYSHORT)
            if breakAt == 'min':
                break
            if sec:
                items.append(str(sec) + ' ' + mls.UI_GENERIC_SECONDVERYSHORT)
            if breakAt == 'sec':
                break
            if ms:
                items.append(str(ms) + ' ' + mls.UI_GENERIC_MILLISECVERYSHORT)
            break
        else:
            if year:
                items.append(str(year) + ' ' + [mls.UI_GENERIC_YEARLOWER, mls.UI_GENERIC_YEARSLOWER][(year > 1)])
            if breakAt == 'year':
                break
            if month:
                items.append(str(month) + ' ' + [mls.UI_GENERIC_MONTHLOWER, mls.UI_GENERIC_MONTHSLOWER][(month > 1)])
            if breakAt == 'month':
                break
            if day:
                items.append(str(day) + ' ' + [mls.UI_GENERIC_DAYLOWER, mls.UI_GENERIC_DAYSLOWER][(day > 1)])
            if breakAt == 'day':
                break
            if hour:
                items.append(str(hour) + ' ' + [mls.UI_GENERIC_HOURLOWER, mls.UI_GENERIC_HOURSLOWER][(hour > 1)])
            if breakAt == 'hour':
                break
            if min:
                items.append(str(min) + ' ' + [mls.UI_GENERIC_MINUTELOWER, mls.UI_GENERIC_MINUTESLOWER][(min > 1)])
            if breakAt == 'min':
                break
            if sec:
                items.append(str(sec) + ' ' + [mls.UI_GENERIC_SECONDLOWER, mls.UI_GENERIC_SECONDSLOWER][(sec > 1)])
            if breakAt == 'sec':
                break
            if ms:
                items.append(str(ms) + ' ' + [mls.UI_GENERIC_MILLISECONDLOWER, mls.UI_GENERIC_MILLISECONDSLOWER][(ms > 1)])
            break

    if items:
        if len(items) == 1:
            return items[0]
        else:
            lastItem = items.pop()
            return ', '.join(items) + ' ' + mls.UI_GENERIC_AND + ' ' + lastItem
    elif breakAt == 'sec':
        return mls.UI_GENERIC_LESSTHANASECOND
    if breakAt == 'min':
        return mls.UI_GENERIC_LESSTHANAMINUTE
    try:
        return getattr(mls, 'UI_GENERIC_LESSTHANA' + breakAt.upper(), '')
    except:
        log.LogError('Missing translation for: UI_GENERIC_' + breakAt.upper())
        return mls.UI_GENERIC_LESSTHANA + breakAt



def FindRussianYearString(year):
    yearInt = int(year)
    yearString = ''
    fmod = math.fmod(yearInt, 10)
    fmods = {1.0: '11',
     2.0: '12',
     3.0: '13',
     4.0: '14'}
    if fmod in fmods:
        specialCase = fmods.get(fmod, None)
        string = str(year)
        if string.endswith(specialCase):
            yearString = mls.UI_GENERIC_YEARSHORT
        else:
            yearString = mls.UI_GENERIC_1YEARSHORT
    else:
        yearString = mls.UI_GENERIC_YEARHORT
    return yearString



def FmtDate(date, fmt = 'll'):
    if date is None:
        return 
    else:
        if fmt == 'nn':
            log.LogTraceback("Incorrect format statement used, 'nn' would result in a return value of None for all input.")
            fmt = 'll'
        if date < 0:
            date *= -1
            neg = '-'
        else:
            neg = ''
        year1800 = const.YEAR365 * 199L
        if date >= year1800 and date % const.DAY and boot.region == 'optic':
            date += 8 * const.HOUR
        (year, month, wd, day, hour, min, sec, ms,) = blue.os.GetTimeParts(date)
        sd = '%d.%.2d.%.2d' % (year, month, day)
        ld = sd
        lt = '%.2d:%.2d:%.2d' % (hour, min, sec)
        if fmt[0] == 'x':
            lt += ':%3d' % ms
        ed = '%d-%.2d-%.2d' % (year, month, day)
        st = lt[:-3]
        if fmt[1] == 'l':
            hrs = lt
        elif fmt[1] == 's':
            hrs = st
        elif fmt[1] == 'n':
            hrs = None
        else:
            raise RuntimeError('InvalidArg', fmt)
        if date % const.DAY == 0:
            hrs = None
        if date < year1800:
            datefmt = None
            days = date / const.DAY
            s = date % const.MIN / const.SEC
            m = date % const.HOUR / const.MIN
            h = date % const.DAY / const.HOUR
            hrs = ''

            def Xtra(value):
                if value != 1:
                    return 's'
                else:
                    return ''


            if fmt[1] == 's':
                if days:
                    hrs = '%d%s' % (days, mls.UI_GENERIC_DAYVERYSHORT)
                if h:
                    hrs = hrs + ' %d%s' % (h, mls.UI_GENERIC_HOURVERYSHORT)
                if m:
                    hrs = hrs + ' %d%s' % (m, mls.UI_GENERIC_MINUTEVERYSHORT)
                if s:
                    hrs = hrs + ' %d%s' % (s, mls.UI_GENERIC_SECONDVERYSHORT)
            else:
                if days:
                    hrs = '%d %s' % (days, [mls.GENERIC_DAY_LOWER, mls.GENERIC_DAYS_LOWER][(days != 1)])
                if h:
                    hrs = hrs + ' %d %s' % (h, [mls.UI_GENERIC_HOUR, mls.UI_GENERIC_HOURS][(h != 1)])
                if m:
                    hrs = hrs + ' %d %s' % (m, [mls.UI_GENERIC_MINUTE, mls.UI_GENERIC_MINUTES][(m != 1)])
                if s or hrs == '':
                    hrs = hrs + ' %d %s' % (s, [mls.UI_GENERIC_SECOND, mls.UI_GENERIC_SECONDS][(s != 1)])
        elif fmt[0] == 'l' or fmt[0] == 'x':
            datefmt = ld
        elif fmt[0] == 's':
            datefmt = sd
        elif fmt[0] == 'n':
            datefmt = None
        elif fmt[0] == 'e':
            datefmt = ed
        else:
            raise RuntimeError('InvalidArg', fmt)
        if datefmt is None and hrs is None:
            return 
        if datefmt is not None and hrs is None:
            return neg + datefmt
        if datefmt is None and hrs is not None:
            return neg + hrs.strip()
        if fmt[0] == 'e':
            return '%s%sT%s.000' % (neg, datefmt, hrs)
        return '%s%s %s' % (neg, datefmt, hrs)


y1800 = const.YEAR365 * 199L

def FmtSimpleDateUTC(date):
    if date is None:
        return 
    (year, month, wd, day, hour, min, sec, ms,) = blue.os.GetTimeParts(date)
    return '%d.%.2d.%.2d %.2d:%.2d:%.2d' % (year,
     month,
     day,
     hour,
     min,
     sec)



def FmtTime(time):
    return '%.2d:%.2d:%.2d' % (time / const.HOUR, time % const.HOUR / const.MIN, time % const.MIN / const.SEC)



def FmtSec(time):
    if not time:
        return '0'
    (h, m, s,) = (time / const.HOUR, time % const.HOUR / const.MIN, time % const.MIN / float(const.SEC))
    return "%.2d:%.2d'%06.3f" % (h, m, s)



def Ess(value):
    if value == 1:
        return ''
    else:
        return 's'



def FmtAmt(amount, fmt = 'ln', showFraction = 0, fillWithZero = 0):
    if amount == None:
        amount = 0
    orgamount = amount
    try:
        amount = long(amount)
    except:
        raise RuntimeError('AmountMustBeInteger', amount)
    minus = ['', '-'][(float(orgamount) < 0.0)]
    fraction = ''
    ret = ''
    fractionNumber = None
    if fmt[0] == 'l':
        if showFraction:
            fraction = abs(math.fmod(orgamount, 1.0))
            fraction = round(fraction, showFraction)
            if fraction >= 1.0:
                amount += [-1, 1][(amount >= 0.0)]
                fraction = 0.0
            fraction = str(fraction)[2:]
            if fillWithZero:
                while len(fraction) < showFraction:
                    fraction += '0'

            fractionNumber = float('%s.%s' % (amount, fraction))
            fraction = DECIMAL + str(fraction)
        digit = ''
        amt = '%d' % abs(amount)
        for i in xrange(len(amt) % 3, len(amt) + 3, 3):
            if i < 3:
                ret = ret + amt[:i]
            else:
                ret = ret + digit + amt[(i - 3):i]
            if i != 0:
                digit = DIGIT

    elif fmt[0] == 's':
        val = abs(amount)
        fractionNumber = val
        if val < 10000.0:
            ret = str(val)
        elif val < 100000.0:
            ret = TruncateAmt(val, long(1000.0)) + [mls.K_FOR_THOUSAND, [mls.THOUSAND.lower(), mls.THOUSANDS.lower()][(str(val)[0] != '1')]][(fmt[1] == 'l')]
        elif val < 100000000.0:
            ret = TruncateAmt(val, long(1000000.0)) + [mls.M_FOR_MILLION, [mls.MILLION.lower(), mls.MILLIONS.lower()][(str(val)[0] != '1')]][(fmt[1] == 'l')]
        if val < 100000000000.0:
            ret = TruncateAmt(val, long(1000000000.0)) + [mls.B_FOR_BILLION, [mls.BILLION.lower(), mls.BILLIONS.lower()][(str(val)[0] != '1')]][(fmt[1] == 'l')]
        elif val < 100000000000000.0:
            ret = TruncateAmt(val, long(1000000000000.0)) + [mls.T_FOR_TRILLION, [mls.TRILLION.lower(), mls.TRILLIONS.lower()][(str(val)[0] != '1')]][(fmt[1] == 'l')]
        else:
            raise UserError('WhatKindOfAmountIsThis', {'amount': amount})
    else:
        ret = '%d' % abs(amount)
    if fractionNumber == 0:
        minus = ''
    return minus + ret + fraction



def TruncateAmt(val, unit):
    rest = val % unit / (unit / 100L)
    ret = str(val / unit)
    if rest > 0:
        ret = ret + '%s%02d' % (DECIMAL, rest)
        if ret[-1:] == '0':
            ret = ret[:-1]
    return ret



def FmtDist(dist, maxdemicals = 3, signed = False):
    if signed and dist < 0.0:
        formatString = '-%s %s'
        dist = abs(dist)
    else:
        formatString = '%s %s'
    dist = max(0, dist)
    if dist < 1.0:
        return '%s %s' % (TruncateDemicals(str(dist)[:5], maxdemicals), mls.M_IN_METER)
    else:
        if dist < 10000.0:
            return '%s %s' % (TruncateDemicals(FmtAmt(long(dist)), maxdemicals), mls.M_IN_METER)
        if dist < 10000000000.0:
            return '%s %s' % (TruncateDemicals(FmtAmt(long(dist / 1000.0)), maxdemicals), mls.KM)
        return '%s %s' % (TruncateDemicals(str(round(dist / const.AU, maxdemicals)), maxdemicals), mls.AU_FOR_LIGHTYEAR)



def FmtDist2(dist, maxDecimals = 3):
    if dist < 0.0:
        dist = abs(dist)
    if dist < 10.0:
        return '%s %s' % (TruncateDemicals(str(dist)[:1], maxDecimals), mls.M_IN_METER)
    else:
        if dist < 100.0:
            return '%s %s' % (TruncateDemicals(str(dist)[:2], maxDecimals), mls.M_IN_METER)
        if dist < 1000.0:
            return '%s %s' % (TruncateDemicals(str(dist)[:3], maxDecimals), mls.M_IN_METER)
        if dist < 10000.0:
            return '%s %s' % (TruncateDemicals(str(dist)[:4], maxDecimals), mls.M_IN_METER)
        if dist < 10000000000.0:
            dist = float(dist) / 1000.0
            return '%s %s' % (TruncateDemicals(str(dist), maxDecimals), mls.KM)
        dist = round(dist / const.AU, maxDecimals)
        return '%s %s' % (TruncateDemicals(str(dist), maxDecimals), mls.AU_FOR_LIGHTYEAR)



def FmtVec(vec, maxdecimals = 3):
    return '[%s, %s, %s]' % (FmtDist(vec[0], maxdecimals, signed=True), FmtDist(vec[1], maxdecimals, signed=True), FmtDist(vec[2], maxdecimals, signed=True))



def TruncateDemicals(dist, maxdemicals):
    if dist.find(DECIMAL) == -1 or maxdemicals is None:
        return dist
    dist = dist.split(DECIMAL)
    dist = DECIMAL.join(dist[:-1]) + DECIMAL + dist[-1][:maxdemicals]
    return dist



def FmtUnit(unit, value, fmt = None):
    if unit == 1:
        return FmtDist(value)
    if unit == 3:
        if fmt is None:
            return FmtDate(value, 'ns')
        else:
            return FmtDate(value, fmt)
    else:
        unitStr = 'mojo'
        value = float(value)
        if value < 1000.0:
            pre = mls.K_FOR_THOUSAND
        else:
            pre = mls.M_FOR_MILLION
        return '%.1f %s%s' % (value, pre, unitStr)



def ParseDate(date):
    if date is None or date == '':
        return 
    if type(date) == unicode:
        date = str(date)
    try:
        date = string.translate(date, __dateseptbl)
        dp = date.split('-', 2)
        return blue.os.GetTimeFromParts(int(dp[0]), int(dp[1]), int(dp[2]), 0, 0, 0, 0)
    except:
        raise UserError('InvalidDate', {'date': date})



def ParseTime(time, isInterval = False):
    if time is None or time == '':
        return 
    try:
        tp = time.split(':', 2)
        time = int(tp[0]) * const.HOUR + int(tp[1]) * const.MIN
        if len(tp) == 3:
            time = time + int(tp[2]) * const.SEC
        if not isInterval and boot.region == 'optic':
            time -= 8 * const.HOUR
            if time < 0:
                time += 24 * const.HOUR
        return time
    except:
        raise UserError('InvalidTime', {'time': time})



def ParseDateTime(dateTime):
    if ' ' in dateTime:
        (d, t,) = dateTime.split(' ')
        dateTime = ParseDate(d)
        dateTime += ParseTime(t)
    else:
        dateTime = ParseDate(dateTime)
    return dateTime



def ParseTimeInterval(time):
    return ParseTime(time, True)



def GetTimeParts(datetime = None, utc = False):
    if datetime is None:
        datetime = blue.os.GetTime()
    if not utc and datetime % const.DAY and boot.region == 'optic':
        datetime += 8 * const.HOUR
    return blue.os.GetTimeParts(datetime)



def CapTimeForDateTime2(time):
    if time < 62798112000000000L:
        time = 62798112000000000L
    elif time > 2650152384000000000L:
        time = 2650152384000000000L
    return time


months = [31,
 59,
 90,
 120,
 151,
 181,
 212,
 243,
 273,
 304,
 334,
 365]
monthsl = [31,
 60,
 91,
 121,
 152,
 182,
 213,
 244,
 274,
 305,
 335,
 366]

def isleap(year):
    return not year % 4



def dateConvert(tmp):
    if isleap(tmp[0]):
        m = monthsl
    else:
        m = months
    result = (tmp[0],
     tmp[1],
     tmp[3],
     tmp[4],
     tmp[5],
     tmp[6],
     tmp[2],
     m[(tmp[1] - 1)] + tmp[3],
     0)
    return result



def ConvertDate(blueTime):
    import time
    return time.mktime(dateConvert(blue.os.GetTimeParts(blueTime)))



def FmtCdkey(cdkey):
    if not cdkey:
        return ''
    return '%s-%s-%s-%s-%s-%s-%s' % (cdkey[0:5],
     cdkey[5:10],
     cdkey[10:15],
     cdkey[15:20],
     cdkey[20:25],
     cdkey[25:30],
     cdkey[30:35])



def LineWrap(s, maxlines, maxlen = 254, pfx = '- '):
    e = len(s)
    if e <= maxlen:
        yield s
    else:
        i = maxlen
        maxlen -= len(pfx)
        maxlines -= 1
        yield s[:i]
        while i < e and maxlines:
            yield pfx + s[i:(i + maxlen)]
            i += maxlen
            maxlines -= 1




def CaseFold(s):
    s2 = s.upper().lower()
    if s2 != s:
        return CaseFold(s2)
    return s2



def CaseFoldCompare(l, r):
    l2 = l.upper().lower()
    r2 = r.upper().lower()
    if l2 != l or r2 != r:
        return CaseFoldCompare(l2, r2)
    return cmp(l, r)



def CaseFoldEquals(l, r):
    return CaseFoldCompare(l, r) == 0



class PasswordString(unicode):
    __guid__ = 'util.PasswordString'

    def __str__(self):
        return '*****'



    def __repr__(self):
        return '*****'




def LFromUI(ui):
    return ui & 4294967295L



def StrFromColor(color):
    return hex(LFromUI(color.AsInt()))



def GetKeyAndNormalize(string):
    key = string
    norm = string
    for c in key:
        if c.isspace():
            key = key.replace(c, '')
            while True:
                prev = norm
                norm = norm.replace(c + c, c)
                if prev == norm:
                    break
                blue.pyos.BeNice()


    key = key.split('\\')[-1]
    return (CaseFold(key), norm)



def SecsFromBlueTimeDelta(t):
    return t / const.SEC



def HoursMinsSecsFromSecs(s):
    s = max(0, s)
    secs = int(s % 60)
    mins = int(s / 60 % 60)
    hours = int(s / 3600)
    return (hours, mins, secs)



def FormatTimeAgo(theTime):
    delta = blue.os.GetTime() - theTime
    (hours, minutes, seconds,) = HoursMinsSecsFromSecs(SecsFromBlueTimeDelta(delta))
    days = 0
    if hours > 48:
        days = int(hours / 24)
        hours %= 24
    t = FormatTimeDelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if t is None:
        howLongAgo = mls.UI_GENERIC_RIGHTNOW
    else:
        howLongAgo = mls.UI_GENERIC_AGO_WITH_FORMAT % {'time': t}
    return howLongAgo



def Plural(n, constant):
    if session.languageID in 'IS':
        if n > 1:
            constant += 'S'
    elif n != 1:
        constant += 'S'
    return getattr(mls, constant)



def Possessive(owner):
    if session.languageID == 'EN':
        if owner.endswith('s'):
            owner += "'"
        else:
            owner += "'s"
    return owner



def FormatTimeDelta(days = None, hours = None, minutes = None, seconds = None):
    ret = []
    if days:
        ret.append('%s %s' % (days, Plural(days, 'UI_GENERIC_DAY').lower()))
    if hours:
        ret.append('%s %s' % (hours, Plural(hours, 'UI_GENERIC_HOUR').lower()))
    if minutes:
        ret.append('%s %s' % (minutes, Plural(minutes, 'UI_GENERIC_MINUTE').lower()))
    if seconds:
        ret.append('%s %s' % (seconds, Plural(seconds, 'UI_GENERIC_SECOND').lower()))
    if ret:
        return ', '.join(ret)
    else:
        return None



def ParseSmallDate(date):
    parsedDate = ParseDate(date)
    if parsedDate > SMALLDATETIME_MIN and parsedDate < SMALLDATETIME_MAX:
        return parsedDate
    raise TypeError('Date is not a legal SmallDateTime value.')



def RomanToInt(roman):
    result = 0
    index = 0
    if not romanNumeralPattern.search(roman):
        raise RuntimeError, 'Invalid Roman numeral: %s' % roman
    for (numeral, length, integer,) in ROMAN_NUMERAL_MAP:
        while roman[index:(index + length)] == numeral:
            result += integer
            index += length


    return result



def IntToRoman(n):
    if not 0 < n < 40:
        raise RuntimeError, 'number out of range (must be 1..4999)'
    if int(n) != n:
        raise RuntimeError, 'non-integers can not be converted'
    result = ''
    for (numeral, length, integer,) in ROMAN_NUMERAL_MAP:
        while n >= integer:
            result += numeral
            n -= integer


    return result



def GetYearMonthFromTime(blueTime):
    t = GetTimeParts(blueTime)
    return (t[0], t[1])



def FormatUrl(url):
    url = url.strip()
    if len(url) and not urlHttpCheck.match(url):
        return 'http://%s' % url
    return url


exports = {'util.GetKeyAndNormalize': GetKeyAndNormalize,
 'util.CaseFoldCompare': CaseFoldCompare,
 'util.CaseFold': CaseFold,
 'util.CaseFoldEquals': CaseFoldEquals,
 'util.LineWrap': LineWrap,
 'util.EscapeSQL': EscapeSQL,
 'util.EscapeAdHocSQL': EscapeAdHocSQL,
 'util.FmtDate': FmtDate,
 'util.FmtSimpleDateUTC': FmtSimpleDateUTC,
 'util.FmtTime': FmtTime,
 'util.FmtSec': FmtSec,
 'util.FmtTimeInterval': FmtTimeInterval,
 'util.FmtAmt': FmtAmt,
 'util.FmtDist': FmtDist,
 'util.FmtDist2': FmtDist2,
 'util.FmtUnit': FmtUnit,
 'util.ParseDate': ParseDate,
 'util.ParseSmallDate': ParseSmallDate,
 'util.ParseTime': ParseTime,
 'util.ParseDateTime': ParseDateTime,
 'util.ParseTimeInterval': ParseTimeInterval,
 'util.GetTimeParts': GetTimeParts,
 'util.CapTimeForDateTime2': CapTimeForDateTime2,
 'util.dateConvert': dateConvert,
 'util.ConvertDate': ConvertDate,
 'util.FmtCdkey': FmtCdkey,
 'util.Ess': Ess,
 'util.StrFromColor': StrFromColor,
 'util.LFromUI': LFromUI,
 'util.RomanToInt': RomanToInt,
 'util.IntToRoman': IntToRoman,
 'util.FmtVec': FmtVec,
 'util.DECIMAL': DECIMAL,
 'util.DIGIT': DIGIT,
 'util.GetYearMonthFromTime': GetYearMonthFromTime,
 'util.FormatUrl': FormatUrl}

