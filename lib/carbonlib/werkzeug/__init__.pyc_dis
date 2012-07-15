#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\__init__.py
from types import ModuleType
import sys
all_by_module = {'werkzeug.debug': ['DebuggedApplication'],
 'werkzeug.local': ['Local',
                    'LocalManager',
                    'LocalProxy',
                    'LocalStack',
                    'release_local'],
 'werkzeug.templates': ['Template'],
 'werkzeug.serving': ['run_simple'],
 'werkzeug.test': ['Client',
                   'EnvironBuilder',
                   'create_environ',
                   'run_wsgi_app'],
 'werkzeug.testapp': ['test_app'],
 'werkzeug.exceptions': ['abort', 'Aborter'],
 'werkzeug.urls': ['url_decode',
                   'url_encode',
                   'url_quote',
                   'url_quote_plus',
                   'url_unquote',
                   'url_unquote_plus',
                   'url_fix',
                   'Href',
                   'iri_to_uri',
                   'uri_to_iri'],
 'werkzeug.formparser': ['parse_form_data'],
 'werkzeug.utils': ['escape',
                    'environ_property',
                    'cookie_date',
                    'http_date',
                    'append_slash_redirect',
                    'redirect',
                    'cached_property',
                    'import_string',
                    'dump_cookie',
                    'parse_cookie',
                    'unescape',
                    'format_string',
                    'find_modules',
                    'header_property',
                    'html',
                    'xhtml',
                    'HTMLBuilder',
                    'validate_arguments',
                    'ArgumentValidationError',
                    'bind_arguments',
                    'secure_filename'],
 'werkzeug.wsgi': ['get_current_url',
                   'get_host',
                   'pop_path_info',
                   'peek_path_info',
                   'SharedDataMiddleware',
                   'DispatcherMiddleware',
                   'ClosingIterator',
                   'FileWrapper',
                   'make_line_iter',
                   'LimitedStream',
                   'responder',
                   'wrap_file',
                   'extract_path_info'],
 'werkzeug.datastructures': ['MultiDict',
                             'CombinedMultiDict',
                             'Headers',
                             'EnvironHeaders',
                             'ImmutableList',
                             'ImmutableDict',
                             'ImmutableMultiDict',
                             'TypeConversionDict',
                             'ImmutableTypeConversionDict',
                             'Accept',
                             'MIMEAccept',
                             'CharsetAccept',
                             'LanguageAccept',
                             'RequestCacheControl',
                             'ResponseCacheControl',
                             'ETags',
                             'HeaderSet',
                             'WWWAuthenticate',
                             'Authorization',
                             'FileMultiDict',
                             'CallbackDict',
                             'FileStorage',
                             'OrderedMultiDict',
                             'ImmutableOrderedMultiDict'],
 'werkzeug.useragents': ['UserAgent'],
 'werkzeug.http': ['parse_etags',
                   'parse_date',
                   'parse_cache_control_header',
                   'is_resource_modified',
                   'parse_accept_header',
                   'parse_set_header',
                   'quote_etag',
                   'unquote_etag',
                   'generate_etag',
                   'dump_header',
                   'parse_list_header',
                   'parse_dict_header',
                   'parse_authorization_header',
                   'parse_www_authenticate_header',
                   'remove_entity_headers',
                   'is_entity_header',
                   'remove_hop_by_hop_headers',
                   'parse_options_header',
                   'dump_options_header',
                   'is_hop_by_hop_header',
                   'unquote_header_value',
                   'quote_header_value',
                   'HTTP_STATUS_CODES'],
 'werkzeug.wrappers': ['BaseResponse',
                       'BaseRequest',
                       'Request',
                       'Response',
                       'AcceptMixin',
                       'ETagRequestMixin',
                       'ETagResponseMixin',
                       'ResponseStreamMixin',
                       'CommonResponseDescriptorsMixin',
                       'UserAgentMixin',
                       'AuthorizationMixin',
                       'WWWAuthenticateMixin',
                       'CommonRequestDescriptorsMixin'],
 'werkzeug.security': ['generate_password_hash', 'check_password_hash'],
 'werkzeug._internal': ['_easteregg']}
attribute_modules = dict.fromkeys(['exceptions', 'routing', 'script'])
object_origins = {}
for module, items in all_by_module.iteritems():
    for item in items:
        object_origins[item] = module

version = None

class module(ModuleType):

    def __getattr__(self, name):
        if name in object_origins:
            module = __import__(object_origins[name], None, None, [name])
            for extra_name in all_by_module[module.__name__]:
                setattr(self, extra_name, getattr(module, extra_name))

            return getattr(module, name)
        if name in attribute_modules:
            __import__('werkzeug.' + name)
        return ModuleType.__getattribute__(self, name)

    def __dir__(self):
        result = list(new_module.__all__)
        result.extend(('__file__', '__path__', '__doc__', '__all__', '__docformat__', '__name__', '__path__', '__package__', '__version__'))
        return result

    @property
    def __version__(self):
        global version
        if version is None:
            try:
                version = __import__('pkg_resources').get_distribution('Werkzeug').version
            except:
                version = 'unknown'

        return version


old_module = sys.modules['werkzeug']
new_module = sys.modules['werkzeug'] = module('werkzeug')
new_module.__dict__.update({'__file__': __file__,
 '__path__': __path__,
 '__doc__': __doc__,
 '__all__': tuple(object_origins) + tuple(attribute_modules),
 '__docformat__': 'restructuredtext en'})