from collections import defaultdict

def SQLStringify(data):
    if isinstance(data, str) or isinstance(data, unicode):
        return "'" + data.replace("'", "''") + "'"
    if data is None:
        return 'NULL'
    if isinstance(data, bool):
        if data:
            return '1'
        else:
            return '0'
    else:
        return str(data)



def TuplesToCSVStrings(tuplelist, numLists, maxOutputLength = 4000):
    if len(tuplelist) == 0:
        return (tuple([ '' for i in xrange(numLists) ]), tuplelist)
    maxstringlen = 0
    workingSet = tuplelist
    remains = []
    for (i, t,) in enumerate(tuplelist):
        strlen = 0
        for e in t:
            if len(str(e)) > strlen:
                strlen = len(str(e))

        maxstringlen += strlen + 1
        if maxstringlen >= maxOutputLength:
            workingSet = tuplelist[:i]
            remains = tuplelist[i:]
            break

    retstrings = []
    for i in range(numLists):
        values = [ v[i] for v in workingSet ]
        retstrings.append(','.join([ str(v) for v in values ]))

    return (tuple(retstrings), remains)



def ExecuteProcInBlocks(proc, **kwargs):
    nonListArgs = dict()
    listArgs = dict()
    listLength = 0
    listName = None
    for (name, value,) in kwargs.iteritems():
        if isinstance(value, (list, tuple)):
            listArgs[name] = value
            listLength = len(value)
            listName = name
        else:
            nonListArgs[name] = value

    stringListArgs = defaultdict(list)
    lengthListArgs = defaultdict(int)
    for i in xrange(listLength):
        singleStringListArgs = dict()
        shouldFlush = False
        for (name, l,) in listArgs.iteritems():
            singleStringListArgs[name] = str(l[i])
            if lengthListArgs[name] + len(singleStringListArgs[name]) >= 8000:
                shouldFlush = True

        if shouldFlush:
            readyKwargs = dict()
            readyKwargs.update(nonListArgs)
            for (name, value,) in stringListArgs.iteritems():
                readyKwargs[name] = ','.join(value)

            proc(**readyKwargs)
            stringListArgs = defaultdict(list)
            lengthListArgs = defaultdict(int)
        for (name, value,) in singleStringListArgs.iteritems():
            stringListArgs[name].append(value)
            lengthListArgs[name] += len(value) + 1


    if listName is not None and len(stringListArgs[listName]) > 0:
        readyKwargs = dict()
        readyKwargs.update(nonListArgs)
        for (name, value,) in stringListArgs.iteritems():
            readyKwargs[name] = ','.join(value)

        proc(**readyKwargs)


import util
exports = util.AutoExports('dbutil', locals())

