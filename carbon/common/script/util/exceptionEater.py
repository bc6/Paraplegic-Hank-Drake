import log
import util

class ExceptionEater(object):

    def __init__(self, message = ''):
        self.message = message



    def __enter__(self):
        pass



    def __exit__(self, eType, eVal, tb):
        if eType is not None:
            log.LogException(exctype=eType, exc=eVal, tb=tb, extraText=self.message)
        return True



exports = {'util.ExceptionEater': ExceptionEater}

