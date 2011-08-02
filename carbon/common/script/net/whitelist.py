import blue
import exceptions
import util
baseWhitelist = '\n    blue.DBRowDescriptor\n    blue.DBRow\n    benchmark.Session\n    benchmark.Snapshot\n    benchmark.ValueDict\n    benchmark.Value\n    benchmark.ValueType\n    ccp_exceptions.SQLError\n    ccp_exceptions.UserError\n    ccp_exceptions.UnmarshalError\n    ccp_exceptions.ConnectionError\n    dbutil.CRowset\n    dbutil.CIndexedRowset\n    dbutil.CFilterRowset\n    exceptions.AttributeError\n    exceptions.IndexError\n    exceptions.ValueError\n    exceptions.KeyError\n    exceptions.WindowsError\n    exceptions.ReferenceError\n    exceptions.RuntimeError\n    exceptions.GPSException\n    exceptions.GPSTransportClosed\n    exceptions.GPSBadAddress\n    exceptions.GPSAddressOccupied\n    exceptions.MachoException\n    exceptions.MachoWrappedException\n    exceptions.ProxyRedirect\n    exceptions.ServiceNotFound\n    exceptions.UberMachoException\n    exceptions.UnMachoDestination\n    exceptions.UnMachoChannel\n    exceptions.WrongMachoNode\n    exceptions.IOError\n    xmlrpclib.Fault\n    macho.CallReq\n    macho.CallRsp\n    macho.ErrorResponse\n    macho.IdentificationReq\n    macho.IdentificationRsp\n    macho.MachoAddress\n    macho.Notification\n    macho.PingReq\n    macho.PingRsp\n    macho.SessionChangeNotification\n    macho.SessionInitialStateNotification\n    macho.TransportClosed\n    macho.MovementNotification\n    objectCaching.CachedMethodCallResult\n    objectCaching.CachedObject\n    objectCaching.CacheOK\n    util.CachedObject\n    util.KeyVal\n    util.Moniker\n    util.PasswordString\n    util.Row\n    util.UpdateMoniker\n    collections.OrderedDict\n    __builtin__.str\n    __builtin__.unicode\n    __builtin__.set\n    collections.defaultdict\n    collections.deque\n    localizationUtil.LocalizationSafeString\n    paperDoll.SculptingRow\n    paperDoll.ModifierRow\n    paperDoll.ColorSelectionRow\n    paperDoll.AppearanceRow\n'

def InitWhitelist():
    wl = baseWhitelist + util.GetGameWhitelist()
    res = {}
    for item in wl.split():
        item.strip()
        if item:
            (mod, obj,) = item.split('.')
            mod = __import__(mod, globals(), locals(), [])
            obj = getattr(mod, obj)
            res[obj] = None

    for e in dir(exceptions):
        if e.endswith('Error'):
            e = getattr(exceptions, e)
            res[e] = None

    blue.marshal.globalsWhitelist = res
    blue.marshal.collectWhitelist = False


exports = {'util.InitWhitelist': InitWhitelist}

