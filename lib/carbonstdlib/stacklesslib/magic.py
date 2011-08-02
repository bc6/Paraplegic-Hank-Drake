import runpy
import os
import sys
from monkeypatch import patch_all
import stackless
from . import main

def run():
    try:
        try:
            if len(sys.argv) > 1:
                target = sys.argv.pop(1)
                if target == '-m' and len(sys.argv) > 1:
                    target = sys.argv.pop(1)
                    runpy.run_module(target, run_name='__main__', alter_sys=True)
                else:
                    runpy.run_path(target, run_name='__main__')
        except Exception:
            main.mainloop.exception = sys.exc_info()
            raise 

    finally:
        main.mainloop.running = False



if __name__ == '__main__':
    patch_all()
    main.set_scheduling_mode(main.SCHEDULING_ROUNDROBIN)
    stackless.tasklet(run)()
    main.mainloop.run()

