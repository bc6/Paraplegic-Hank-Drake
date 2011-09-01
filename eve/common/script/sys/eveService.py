import service
import types
ROLE_DUST = 1L
ROLE_BANNING = 2L
ROLE_MARKET = 4L
ROLE_MARKETH = 8L
ROLE_CSMADMIN = 16L
ROLE_CSMDELEGATE = 32L
ROLE_EXPOPLAYER = 64L
ROLE_PETITIONEE = 256L
ROLE_CENTURION = 2048L
ROLE_WORLDMOD = 4096L
ROLE_LEGIONEER = 262144L
ROLE_HEALSELF = 4194304L
ROLE_HEALOTHERS = 8388608L
ROLE_NEWSREPORTER = 16777216L
ROLE_SPAWN = 8589934592L
ROLE_WIKIEDITOR = 68719476736L
ROLE_TRANSFER = 137438953472L
ROLE_GMS = 274877906944L
service.ROLEMASK_ELEVATEDPLAYER = service.ROLEMASK_ELEVATEDPLAYER & ~ROLE_NEWSREPORTER
exports = {}
consts = {}
for i in globals().items():
    if type(i[1]) in (types.IntType, types.LongType):
        exports['service.' + i[0]] = i[1]
        consts[i[0]] = i[1]


def _MachoResolveAdditional(self, sess):
    if self.__machoresolve__ is not None:
        mn = sm.services['machoNet']
        if not sess.role & service.ROLE_SERVICE:
            if self.__machoresolve__ == 'station':
                if not sess.stationid:
                    return 'You must be located at a station to use this service'
                return mn.GetNodeFromAddress('station', sess.stationid)
            if self.__machoresolve__ == 'solarsystem':
                if not sess.solarsystemid:
                    return 'You must be located in a solar system to use this service'
                return mn.GetNodeFromAddress(const.cluster.SERVICE_BEYONCE, sess.solarsystemid)
            if self.__machoresolve__ == 'solarsystem2':
                if not sess.solarsystemid2:
                    return 'Your location must belong to a known solarsystem'
                return mn.GetNodeFromAddress(const.cluster.SERVICE_BEYONCE, sess.solarsystemid2)
            if self.__machoresolve__ in ('location', 'locationPreferred'):
                if not sess.locationid:
                    if self.__machoresolve__ == 'locationPreferred':
                        return 
                    return 'You must be located in a solar system or at station to use this service'
                if sess.solarsystemid:
                    return mn.GetNodeFromAddress(const.cluster.SERVICE_BEYONCE, sess.solarsystemid)
                if session.stationid:
                    return mn.GetNodeFromAddress('station', sess.stationid)
                raise RuntimeError('machoresolving a location bound service with without a location session')
            elif self.__machoresolve__ in ('character',):
                if sess.charid is None:
                    return 
                else:
                    return mn.GetNodeFromAddress(const.cluster.SERVICE_CHARACTER, sess.charid % const.CHARNODE_MOD)
            elif self.__machoresolve__ in ('corporation',):
                if sess.corpid is None:
                    return 'You must have a corpid in your session to use this service'
                else:
                    return mn.GetNodeFromAddress(const.cluster.SERVICE_CHATX, sess.corpid % 200)
            elif self.__machoresolve__ == 'bulk':
                if sess.userid is None:
                    return 'You must have a userid in your session to use this service'
                return mn.GetNodeFromAddress(const.cluster.SERVICE_BULK, sess.userid % const.BULKNODE_MOD)
            raise RuntimeError('This service is crap (%s)' % self.__logname__)



class EveService(service.CoreService):
    pass
exports.update({'service._MachoResolveAdditional': _MachoResolveAdditional,
 'service.Service': EveService,
 'service.consts': consts})

