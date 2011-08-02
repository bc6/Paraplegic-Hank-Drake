import sys
import logUE3
sys.ue3 = True

class LogStream:

    def __init__(self, flag):
        self.flag = flag
        self.buff = []



    def write(self, s):
        self.buff.append(s)
        if '\n' in s:
            for line in ''.join(self.buff).splitlines():
                if line:
                    logUE3.Log('[PyCON]%s' % (line,), self.flag)

            del self.buff[:]




def Run():
    sys.__stdout__ = sys.stdout = LogStream('i')
    sys.__stderr__ = sys.stderr = LogStream('e')
    GAMEHOME = None
    upperCase = False
    for sysPath in sys.path:
        idx = sysPath.lower().find('common.zip')
        if idx > -1:
            GAMEHOME = sysPath[:idx]
            s = sysPath[idx:]
            if s.upper() == s:
                upperCase = True
            break

    print 'GAMEHOME',
    print GAMEHOME
    PACKAGES = ['python27.zip', 'deelite.zip', 'common.zip']
    if upperCase:
        PACKAGES = [ s.upper() for s in PACKAGES ]
    if sys.platform == 'win32' and sys.hasPyCompiler:
        sys.path = ['../../../tool/bin']
        import sitecustomize
        sys.packaged = False
        import libpaths
        libPackages = set((pgk['pkgName'] for pgk in libpaths.PACKAGES))
        if not set(PACKAGES) <= libPackages:
            raise RuntimeError('Package definitions differ! Please fix', libPackages, set(PACKAGES))
        print 'Python using file modules. sys.path:'
        for p in sys.path:
            print '\t',
            print p

    else:
        sys.packaged = True
        sys.path = [ GAMEHOME + pkg for pkg in PACKAGES ]
        print 'Python using packaged modules:',
        print sys.path



