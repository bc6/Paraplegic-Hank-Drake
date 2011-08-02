from datetime import timedelta, time, date
from time import localtime
import string
__all__ = ['parse_timedelta',
 'normalize_timedelta',
 'parse_time',
 'normalize_time',
 'parse_date',
 'normalize_date']

def _number(val):
    try:
        return string.atoi(val)
    except:
        return None



def parse_timedelta(val):
    if not val:
        return None
    val = string.lower(val)
    if '.' in val:
        val = float(val)
        return timedelta(hours=int(val), minutes=60 * (val % 1.0))
    fHour = 'h' in val or ':' in val
    fMin = 'm' in val or ':' in val
    fFraction = '.' in val
    for noise in 'minu:teshour()':
        val = string.replace(val, noise, ' ')

    val = string.strip(val)
    val = string.split(val)
    hr = 0.0
    mi = 0
    val.reverse()
    if fHour:
        hr = int(val.pop())
    if fMin:
        mi = int(val.pop())
    if len(val) > 0 and not hr:
        hr = int(val.pop())
    return timedelta(hours=hr, minutes=mi)



def normalize_timedelta(val):
    if type(val) == str:
        val = parse_timedelta(val)
    if not val:
        return ''
    hr = val.seconds / 3600
    mn = val.seconds % 3600 / 60
    return '%d.%02d' % (hr, mn * 100 / 60)



def parse_time(val):
    if not val:
        return None
    hr = mi = 0
    val = string.lower(val)
    amflag = -1 != string.find(val, 'a')
    pmflag = -1 != string.find(val, 'p')
    for noise in ':amp.':
        val = string.replace(val, noise, ' ')

    val = string.split(val)
    if len(val) > 1:
        hr = int(val[0])
        mi = int(val[1])
    else:
        val = val[0]
        if len(val) < 1:
            pass
        elif 'now' == val:
            tm = localtime()
            hr = tm[3]
            mi = tm[4]
        elif 'noon' == val:
            hr = 12
        elif len(val) < 3:
            hr = int(val)
            if not amflag and not pmflag and hr < 7:
                hr += 12
        elif len(val) < 5:
            hr = int(val[:-2])
            mi = int(val[-2:])
        else:
            hr = int(val[:1])
    if amflag and hr >= 12:
        hr = hr - 12
    if pmflag and hr < 12:
        hr = hr + 12
    return time(hr, mi)



def normalize_time(value, ampm):
    if not value:
        return ''
    if type(value) == str:
        value = parse_time(value)
    if not ampm:
        return '%02d:%02d' % (value.hour, value.minute)
    hr = value.hour
    am = 'AM'
    if hr < 1 or hr > 23:
        hr = 12
    elif hr >= 12:
        am = 'PM'
        if hr > 12:
            hr = hr - 12
    return '%02d:%02d %s' % (hr, value.minute, am)


_one_day = timedelta(days=1)
_str2num = {'jan': 1,
 'feb': 2,
 'mar': 3,
 'apr': 4,
 'may': 5,
 'jun': 6,
 'jul': 7,
 'aug': 8,
 'sep': 9,
 'oct': 10,
 'nov': 11,
 'dec': 12}

def _month(val):
    for (key, mon,) in _str2num.items():
        if key in val:
            return mon

    raise TypeError("unknown month '%s'" % val)


_days_in_month = {1: 31,
 2: 28,
 3: 31,
 4: 30,
 5: 31,
 6: 30,
 7: 31,
 8: 31,
 9: 30,
 10: 31,
 11: 30,
 12: 31}
_num2str = {1: 'Jan',
 2: 'Feb',
 3: 'Mar',
 4: 'Apr',
 5: 'May',
 6: 'Jun',
 7: 'Jul',
 8: 'Aug',
 9: 'Sep',
 10: 'Oct',
 11: 'Nov',
 12: 'Dec'}
_wkdy = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')

def parse_date(val):
    if not val:
        return 
    val = string.lower(val)
    now = None
    strict = val.split('-')
    if len(strict) == 3:
        (y, m, d,) = strict
        if '+' in d:
            d = d.split('+')[0]
        if ' ' in d:
            d = d.split(' ')[0]
        try:
            now = date(int(y), int(m), int(d))
            val = 'xxx' + val[10:]
        except ValueError:
            pass
    if not now:
        chk = val[:3]
        if chk in ('now', 'tod'):
            now = date.today()
        elif chk in _wkdy:
            now = date.today()
            idx = list(_wkdy).index(chk) + 1
            while now.isoweekday() != idx:
                now += _one_day

    if now:
        tail = val[3:].strip()
        tail = tail.replace('+', ' +').replace('-', ' -')
        for item in tail.split():
            try:
                days = int(item)
            except ValueError:
                pass
            else:
                now += timedelta(days=days)

        return now
    yr = mo = dy = None
    for noise in ('/', '-', ',', '*'):
        val = string.replace(val, noise, ' ')

    for noise in _wkdy:
        val = string.replace(val, noise, ' ')

    out = []
    last = False
    ldig = False
    for ch in val:
        if ch.isdigit():
            if last and not ldig:
                out.append(' ')
            last = ldig = True
        elif ldig:
            out.append(' ')
            ldig = False
        last = True
        out.append(ch)

    val = string.split(''.join(out))
    if 3 == len(val):
        a = _number(val[0])
        b = _number(val[1])
        c = _number(val[2])
        if len(val[0]) == 4:
            yr = a
            if b:
                mo = b
                dy = c
            else:
                mo = _month(val[1])
            dy = c
        elif a > 0:
            yr = c
            if len(val[2]) < 4:
                raise TypeError('four digit year required')
            if b:
                dy = b
                mo = a
            else:
                dy = a
            mo = _month(val[1])
        else:
            dy = b
            yr = c
            if len(val[2]) < 4:
                raise TypeError('four digit year required')
        mo = _month(val[0])
    elif 2 == len(val):
        a = _number(val[0])
        b = _number(val[1])
        if a > 999:
            yr = a
            dy = 1
            if b > 0:
                mo = b
            else:
                mo = _month(val[1])
        elif a > 0:
            if b > 999:
                mo = a
                yr = b
                dy = 1
            elif b > 0:
                mo = a
                dy = b
            else:
                dy = a
                mo = _month(val[1])
        elif b > 999:
            yr = b
            dy = 1
        else:
            dy = b
        mo = _month(val[0])
    elif 1 == len(val):
        val = val[0]
        if not val.isdigit():
            mo = _month(val)
            if mo is not None:
                dy = 1
        else:
            v = _number(val)
            val = str(v)
            if 8 == len(val):
                yr = _number(val[:4])
                mo = _number(val[4:6])
                dy = _number(val[6:])
        if len(val) in (3, 4):
            if v > 1300:
                yr = v
                mo = 1
                dy = 1
            else:
                mo = _number(val[:-2])
                dy = _number(val[-2:])
        elif v < 32:
            dy = v
        else:
            raise TypeError('four digit year required')
    tm = localtime()
    if mo is None:
        mo = tm[1]
    if dy is None:
        dy = tm[2]
    if yr is None:
        yr = tm[0]
    return date(yr, mo, dy)



def normalize_date(val, iso8601 = True):
    if not val:
        return ''
    if type(val) == str:
        val = parse_date(val)
    if iso8601:
        return '%4d-%02d-%02d' % (val.year, val.month, val.day)
    return '%02d %s %4d' % (val.day, _num2str[val.month], val.year)



