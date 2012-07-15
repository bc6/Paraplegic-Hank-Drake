#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\stacklesslib\replacements\select.py
from __future__ import absolute_import
import stackless
import stacklesslib.util
import select as real_select
error = real_select.error
__doc__ = real_select.__doc__
_main_thread_id = stackless.main.thread_id

def select(*args, **kwargs):
    if stackless.current.thread_id == _main_thread_id:
        if len(args) == 3 or len(args) == 4 and (args[3] is None or args[3] > 0.05) or 'timeout' in kwargs and (kwargs['timeout'] is None or kwargs['timeout'] > 0.05):
            return stacklesslib.util.call_on_thread(real_select.select, args, kwargs)
    return real_select.select(*args)


select.__doc__ = real_select.select.__doc__