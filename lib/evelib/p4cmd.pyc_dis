#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\eve\common\lib\p4cmd.py
import subprocess, marshal, sys

class P4Error(RuntimeError):

    def __init__(self, res):
        RuntimeError.__init__(self, res['data'])
        self.generic = res['generic']
        self.severity = res['severity']


class Bunch(dict):
    __slots__ = []

    def __repr__(self):
        return 'Bunch of %s' % dict.__repr__(self)

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getstate__(self):
        pass

    def Copy(self):
        return Bunch(self.copy())


def Run(cmd, extra = ''):
    p = subprocess.Popen('p4 -G %s %s' % (extra, cmd), stdout=subprocess.PIPE)
    try:
        while True:
            res = marshal.load(p.stdout)
            if res.get('code', None) == 'error':
                raise P4Error(res)
            yield Bunch(res)

    except EOFError:
        pass


def Describe(changelist, flags = ''):
    desc = Run('describe %s %s' % (changelist, flags)).next()
    files = []
    i = 0
    while True:
        no = str(i)
        i += 1
        if 'depotFile' + no in desc:
            file = [desc['depotFile' + no],
             desc['rev' + no],
             desc['action' + no],
             desc['type' + no]]
            files.append(file)
        else:
            break

    res = Bunch(status=desc.status, code=desc.code, client=desc.client, user=desc.user, time=float(desc.time), change=int(desc.change), desc=desc.desc, files=files)
    return res


if __name__ == '__main__':
    for res in Run(' '.join(sys.argv[1:])):
        for k, v in res.items():
            print '%s\t%s' % (k, v)