import re
__all__ = ['interval_decode', 'interval_encode']
second = 1
minute = second * 60
hour = minute * 60
day = hour * 24
week = day * 7
month = day * 30
year = day * 365
timeValues = {'y': year,
 'b': month,
 'w': week,
 'd': day,
 'h': hour,
 'm': minute,
 's': second}
timeOrdered = timeValues.items()
timeOrdered.sort(lambda a, b: -cmp(a[1], b[1]))

def interval_encode(seconds, include_sign = False):
    s = ''
    orig = seconds
    seconds = abs(seconds)
    for (char, amount,) in timeOrdered:
        if seconds >= amount:
            (i, seconds,) = divmod(seconds, amount)
            s += '%i%s' % (i, char)

    if orig < 0:
        s = '-' + s
    elif not orig:
        return '0'
    if include_sign:
        s = '+' + s
    return s


_timeRE = re.compile('[0-9]+[a-zA-Z]')

def interval_decode(s):
    time = 0
    sign = 1
    s = s.strip()
    if s.startswith('-'):
        s = s[1:]
        sign = -1
    elif s.startswith('+'):
        s = s[1:]
    for match in allMatches(s, _timeRE):
        char = match.group(0)[-1].lower()
        if not timeValues.has_key(char):
            continue
        time += int(match.group(0)[:-1]) * timeValues[char]

    return time



def allMatches(source, regex):
    pos = 0
    end = len(source)
    rv = []
    match = regex.search(source, pos)
    while match:
        rv.append(match)
        match = regex.search(source, match.end())

    return rv


if __name__ == '__main__':
    import doctest
    doctest.testmod()

