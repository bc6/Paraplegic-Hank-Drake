import trinity

def LoadTrinityObject(resPath, urgent = False):
    if urgent:
        triObject = trinity.LoadUrgent(resPath)
    else:
        triObject = trinity.Load(resPath)
    if triObject and triObject.__bluetype__.endswith('Res'):
        triObject = eval(triObject.__bluetype__.replace('Res', '()'))
        if triObject.__bluetype__ not in const.world.BLUETYPE_TO_RESPATH_ATTRNAME:
            raise RunTimeError('Object Type %s not supported' % triObject.__bluetype__)
        setattr(triObject, const.world.BLUETYPE_TO_RESPATH_ATTRNAME[triObject.__bluetype__], str(resPath))
    return triObject


exports = {'util.LoadTrinityObject': LoadTrinityObject}

