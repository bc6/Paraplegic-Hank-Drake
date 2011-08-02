import uicls
import log
from uicls import Base

def ExposeCoreClassesWithOutCorePostfix():
    for (className, classInstance,) in uicls.__dict__.items():
        if not className.endswith('Core'):
            continue
        if not issubclass(classInstance, Base):
            continue
        nocore = className[:-4]
        if nocore not in uicls.__dict__:
            uicls.__dict__[nocore] = classInstance
            log.LogInfo('Added %s into uicls namespace as %s' % (className, nocore))




def CheckFunctionOverwrite(fatalOnly = True):
    fatal = ['_OnClose', '_OnResize', '_OnDestroy']
    for (className, classInstance,) in uicls.__dict__.items():
        if not getattr(classInstance, '__bases__', None):
            continue
        for (k, v,) in classInstance.__dict__.iteritems():
            if k.endswith('_'):
                continue
            if not hasattr(v, 'func_code'):
                continue
            if k not in v.func_code.co_names and k in dir(classInstance.__bases__[-1]):
                if k in fatal:
                    print 'Bad overwrite in class:',
                    print className,
                    print 'function name:',
                    print k
                elif not fatalOnly:
                    print 'Possible bad overwrite in class:',
                    print className,
                    print 'function name:',
                    print k


    print 'CheckFunctionOverwrite done'


exports = {'uicls._ExposeCoreClassesWithOutCorePostfix': ExposeCoreClassesWithOutCorePostfix,
 'uicls.CheckFunctionOverwrite': CheckFunctionOverwrite}

