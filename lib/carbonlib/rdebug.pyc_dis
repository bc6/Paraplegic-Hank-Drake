#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\rdebug.py
import traceback, stackless

class DebugFile(object):

    def write(self, line):
        import blue
        blue.pyos.OutputDebugString(line)

    def writelines(self, lines):
        for line in lines:
            self.write(line)


def Traceback(tasklet = None):
    if not tasklet:
        tasklet = stackless.getcurrent()
    print >> file, 'traceback for tasklet %s' % tasklet
    traceback.print_stack(f=tasklet.frame)


def Tasklets():
    t = stackless.getcurrent()
    r = [t]
    while t.next and t.next != r[0]:
        t = t.next
        r.append(t)

    t = stackless.getmain()
    if t not in r:
        r.append(t)
        while t.next and t.next != stackless.getmain():
            t = t.next
            r.append(t)

    return r


def TracebackAll():
    for t in Tasklets():
        if t != stackless.getmain():
            Traceback(tasklet=t)


def RedirectOutput():
    debugFile = DebugFile()
    import sys
    sys.stdout = debugFile
    sys.stderr = debugFile


def Quote(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\t', '\\t')
    s = s.replace('\n', '\\n')
    return '"' + s + '"'


def GetModuleText(module = None):
    if module:
        f = module.__file__
    else:
        f = __file__
    f = f.replace('.pyc', '.py').replace('.pyo', '.py')
    return file(f).read().rstrip() + '\n'


def GetModuleString(module = None):
    return Quote(GetModuleText(module))