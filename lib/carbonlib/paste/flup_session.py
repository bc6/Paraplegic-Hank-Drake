from paste import httpexceptions
from paste import wsgilib
import flup.middleware.session
flup_session = flup.middleware.session
store_cache = {}

class NoDefault(object):
    pass

class SessionMiddleware(object):
    session_classes = {'memory': (flup_session.MemorySessionStore, [('session_timeout',
                  'timeout',
                  int,
                  60)]),
     'disk': (flup_session.DiskSessionStore, [('session_timeout',
                'timeout',
                int,
                60), ('session_dir',
                'storeDir',
                str,
                '/tmp/sessions')]),
     'shelve': (flup_session.ShelveSessionStore, [('session_timeout',
                  'timeout',
                  int,
                  60), ('session_file',
                  'storeFile',
                  str,
                  '/tmp/session.shelve')])}

    def __init__(self, app, global_conf = None, session_type = NoDefault, cookie_name = NoDefault, **store_config):
        self.application = app
        if session_type is NoDefault:
            session_type = global_conf.get('session_type', 'disk')
        self.session_type = session_type
        try:
            (self.store_class, self.store_args,) = self.session_classes[self.session_type]
        except KeyError:
            raise KeyError('The session_type %s is unknown (I know about %s)' % (self.session_type, ', '.join(self.session_classes.keys())))
        kw = {}
        for (config_name, kw_name, coercer, default,) in self.store_args:
            value = coercer(store_config.get(config_name, default))
            kw[kw_name] = value

        self.store = self.store_class(**kw)
        if cookie_name is NoDefault:
            cookie_name = global_conf.get('session_cookie', '_SID_')
        self.cookie_name = cookie_name



    def __call__(self, environ, start_response):
        service = flup_session.SessionService(self.store, environ, cookieName=self.cookie_name, fieldName=self.cookie_name)
        environ['paste.flup_session_service'] = service

        def cookie_start_response(status, headers, exc_info = None):
            service.addCookie(headers)
            return start_response(status, headers, exc_info)


        try:
            app_iter = self.application(environ, cookie_start_response)
        except httpexceptions.HTTPException as e:
            headers = (e.headers or {}).items()
            service.addCookie(headers)
            e.headers = dict(headers)
            service.close()
            raise 
        except:
            service.close()
            raise 
        return wsgilib.add_close(app_iter, service.close)




def make_session_middleware(app, global_conf, session_type = NoDefault, cookie_name = NoDefault, **store_config):
    return SessionMiddleware(app, global_conf=global_conf, session_type=session_type, cookie_name=cookie_name, **store_config)



