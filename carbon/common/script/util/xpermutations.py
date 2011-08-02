
def xcombinations(items, n):
    if n == 0:
        yield []
    else:
        for i in xrange(len(items)):
            for cc in xcombinations(items[:i] + items[(i + 1):], n - 1):
                yield [items[i]] + cc





def xuniqueCombinations(items, n):
    if n == 0:
        yield []
    else:
        for i in xrange(len(items)):
            for cc in xuniqueCombinations(items[(i + 1):], n - 1):
                yield [items[i]] + cc





def xselections(items, n):
    if n == 0:
        yield []
    else:
        for i in xrange(len(items)):
            for ss in xselections(items, n - 1):
                yield [items[i]] + ss





def xpermutations(items):
    return xcombinations(items, len(items))


exports = {'util.xcombinations': xcombinations,
 'util.xuniqueCombinations': xuniqueCombinations,
 'util.xselections': xselections,
 'util.xpermutations': xpermutations}

