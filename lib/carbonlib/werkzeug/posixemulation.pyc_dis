#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\posixemulation.py
import os
import errno
import time
import random
can_rename_open_file = False
if os.name == 'nt':
    _rename = lambda src, dst: False
    _rename_atomic = lambda src, dst: False
    try:
        import ctypes
        _MOVEFILE_REPLACE_EXISTING = 1
        _MOVEFILE_WRITE_THROUGH = 8
        _MoveFileEx = ctypes.windll.kernel32.MoveFileExW

        def _rename(src, dst):
            if not isinstance(src, unicode):
                src = unicode(src, sys.getfilesystemencoding())
            if not isinstance(dst, unicode):
                dst = unicode(dst, sys.getfilesystemencoding())
            if _rename_atomic(src, dst):
                return True
            retry = 0
            rv = False
            while not rv and retry < 100:
                rv = _MoveFileEx(src, dst, _MOVEFILE_REPLACE_EXISTING | _MOVEFILE_WRITE_THROUGH)
                if not rv:
                    time.sleep(0.001)
                    retry += 1

            return rv


        _CreateTransaction = ctypes.windll.ktmw32.CreateTransaction
        _CommitTransaction = ctypes.windll.ktmw32.CommitTransaction
        _MoveFileTransacted = ctypes.windll.kernel32.MoveFileTransactedW
        _CloseHandle = ctypes.windll.kernel32.CloseHandle
        can_rename_open_file = True

        def _rename_atomic(src, dst):
            ta = _CreateTransaction(None, 0, 0, 0, 0, 1000, 'Werkzeug rename')
            if ta == -1:
                return False
            try:
                retry = 0
                rv = False
                while not rv and retry < 100:
                    rv = _MoveFileTransacted(src, dst, None, None, _MOVEFILE_REPLACE_EXISTING | _MOVEFILE_WRITE_THROUGH, ta)
                    if rv:
                        rv = _CommitTransaction(ta)
                        break
                    else:
                        time.sleep(0.001)
                        retry += 1

                return rv
            finally:
                _CloseHandle(ta)


    except Exception:
        pass

    def rename(src, dst):
        if _rename(src, dst):
            return
        try:
            os.rename(src, dst)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise 
            old = '%s-%08x' % (dst, random.randint(0, sys.maxint))
            os.rename(dst, old)
            os.rename(src, dst)
            try:
                os.unlink(old)
            except Exception:
                pass


else:
    rename = os.rename
    can_rename_open_file = True