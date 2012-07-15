#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/autoexport.py
import types

def AutoExports(namespace, globals_):
    return dict([ ('%s.%s' % (namespace, name), val) for name, val in globals_.iteritems() if not name.startswith('_') and not isinstance(val, types.ModuleType) and not hasattr(val, '__guid__') ])


exports = AutoExports('util', locals())