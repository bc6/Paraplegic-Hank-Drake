try:
    set
except NameError:
    from sets import Set as set
import cherrypy
from cherrypy.lib import reprconf
NamespaceSet = reprconf.NamespaceSet

def merge(base, other):
    if isinstance(other, basestring):
        cherrypy.engine.autoreload.files.add(other)
    for (section, value_map,) in reprconf.as_dict(other).items():
        if not isinstance(value_map, dict):
            raise ValueError("Application config must include section headers, but the config you tried to merge doesn't have any sections. Wrap your config in another dict with paths as section headers, for example: {'/': config}.")
        base.setdefault(section, {}).update(value_map)




class Config(reprconf.Config):

    def update(self, config):
        if isinstance(config, basestring):
            cherrypy.engine.autoreload.files.add(config)
        reprconf.Config.update(self, config)



    def _apply(self, config):
        if isinstance(config.get('global', None), dict):
            if len(config) > 1:
                cherrypy.checker.global_config_contained_paths = True
            config = config['global']
        if 'tools.staticdir.dir' in config:
            config['tools.staticdir.section'] = 'global'
        reprconf.Config._apply(self, config)



    def __call__(self, *args, **kwargs):
        if args:
            raise TypeError('The cherrypy.config decorator does not accept positional arguments; you must use keyword arguments.')

        def tool_decorator(f):
            if not hasattr(f, '_cp_config'):
                f._cp_config = {}
            for (k, v,) in kwargs.items():
                f._cp_config[k] = v

            return f


        return tool_decorator



Config.environments = environments = {'staging': {'engine.autoreload_on': False,
             'checker.on': False,
             'tools.log_headers.on': False,
             'request.show_tracebacks': False,
             'request.show_mismatched_params': False},
 'production': {'engine.autoreload_on': False,
                'checker.on': False,
                'tools.log_headers.on': False,
                'request.show_tracebacks': False,
                'request.show_mismatched_params': False,
                'log.screen': False},
 'embedded': {'engine.autoreload_on': False,
              'checker.on': False,
              'tools.log_headers.on': False,
              'request.show_tracebacks': False,
              'request.show_mismatched_params': False,
              'log.screen': False,
              'engine.SIGHUP': None,
              'engine.SIGTERM': None},
 'test_suite': {'engine.autoreload_on': False,
                'checker.on': False,
                'tools.log_headers.on': False,
                'request.show_tracebacks': True,
                'request.show_mismatched_params': True,
                'log.screen': False}}

def _server_namespace_handler(k, v):
    atoms = k.split('.', 1)
    if len(atoms) > 1:
        if not hasattr(cherrypy, 'servers'):
            cherrypy.servers = {}
        (servername, k,) = atoms
        if servername not in cherrypy.servers:
            from cherrypy import _cpserver
            cherrypy.servers[servername] = _cpserver.Server()
            cherrypy.servers[servername].subscribe()
        if k == 'on':
            if v:
                cherrypy.servers[servername].subscribe()
            else:
                cherrypy.servers[servername].unsubscribe()
        else:
            setattr(cherrypy.servers[servername], k, v)
    else:
        setattr(cherrypy.server, k, v)


Config.namespaces['server'] = _server_namespace_handler

def _engine_namespace_handler(k, v):
    engine = cherrypy.engine
    if k == 'autoreload_on':
        if v:
            engine.autoreload.subscribe()
        else:
            engine.autoreload.unsubscribe()
    elif k == 'autoreload_frequency':
        engine.autoreload.frequency = v
    elif k == 'autoreload_match':
        engine.autoreload.match = v
    elif k == 'reload_files':
        engine.autoreload.files = set(v)
    elif k == 'deadlock_poll_freq':
        engine.timeout_monitor.frequency = v
    elif k == 'SIGHUP':
        engine.listeners['SIGHUP'] = set([v])
    elif k == 'SIGTERM':
        engine.listeners['SIGTERM'] = set([v])
    elif '.' in k:
        (plugin, attrname,) = k.split('.', 1)
        plugin = getattr(engine, plugin)
        if attrname == 'on':
            if v and hasattr(getattr(plugin, 'subscribe', None), '__call__'):
                plugin.subscribe()
                return 
            if not v and hasattr(getattr(plugin, 'unsubscribe', None), '__call__'):
                plugin.unsubscribe()
                return 
        setattr(plugin, attrname, v)
    else:
        setattr(engine, k, v)


Config.namespaces['engine'] = _engine_namespace_handler

def _tree_namespace_handler(k, v):
    cherrypy.tree.graft(v, v.script_name)
    cherrypy.engine.log('Mounted: %s on %s' % (v, v.script_name or '/'))


Config.namespaces['tree'] = _tree_namespace_handler

