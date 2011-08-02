from cStringIO import StringIO
import traceback
import threading
import pdb
import sys
exec_lock = threading.Lock()

class EvalContext(object):

    def __init__(self, namespace, globs):
        self.namespace = namespace
        self.globs = globs



    def exec_expr(self, s):
        out = StringIO()
        exec_lock.acquire()
        save_stdout = sys.stdout
        try:
            debugger = _OutputRedirectingPdb(save_stdout)
            debugger.reset()
            pdb.set_trace = debugger.set_trace
            sys.stdout = out
            try:
                code = compile(s, '<web>', 'single', 0, 1)
                exec code in self.namespace, self.globs
                debugger.set_continue()
            except KeyboardInterrupt:
                raise 
            except:
                traceback.print_exc(file=out)
                debugger.set_continue()

        finally:
            sys.stdout = save_stdout
            exec_lock.release()

        return out.getvalue()




class _OutputRedirectingPdb(pdb.Pdb):

    def __init__(self, out):
        self._OutputRedirectingPdb__out = out
        pdb.Pdb.__init__(self)



    def trace_dispatch(self, *args):
        save_stdout = sys.stdout
        sys.stdout = self._OutputRedirectingPdb__out
        try:
            return pdb.Pdb.trace_dispatch(self, *args)

        finally:
            sys.stdout = save_stdout





