
def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ('true', 'yes', 'on', 'y', 't', '1'):
            return True
        if obj in ('false', 'no', 'off', 'n', 'f', '0'):
            return False
        raise ValueError('String is not true/false: %r' % obj)
    return bool(obj)



def aslist(obj, sep = None, strip = True):
    if isinstance(obj, (str, unicode)):
        lst = obj.split(sep)
        if strip:
            lst = [ v.strip() for v in lst ]
        return lst
    else:
        if isinstance(obj, (list, tuple)):
            return obj
        if obj is None:
            return []
        return [obj]



