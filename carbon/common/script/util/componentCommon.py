
def UnpackStringToTuple(string, conversionFunc = None):
    elementList = eval(string)
    if conversionFunc is not None:
        elementList = [ conversionFunc(element) for element in elementList ]
    return tuple(elementList)


exports = {'util.UnpackStringToTuple': UnpackStringToTuple}

