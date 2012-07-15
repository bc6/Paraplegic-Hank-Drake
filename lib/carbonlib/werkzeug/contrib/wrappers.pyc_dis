#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\wrappers.py
import codecs
from werkzeug.exceptions import BadRequest
from werkzeug.utils import cached_property
from werkzeug.http import dump_options_header, parse_options_header
from werkzeug._internal import _decode_unicode
try:
    from simplejson import loads
except ImportError:
    from json import loads

def is_known_charset(charset):
    try:
        codecs.lookup(charset)
    except LookupError:
        return False

    return True


class JSONRequestMixin(object):

    @cached_property
    def json(self):
        if 'json' not in self.environ.get('CONTENT_TYPE', ''):
            raise BadRequest('Not a JSON request')
        try:
            return loads(self.data)
        except Exception:
            raise BadRequest('Unable to read JSON request')


class ProtobufRequestMixin(object):
    protobuf_check_initialization = True

    def parse_protobuf(self, proto_type):
        if 'protobuf' not in self.environ.get('CONTENT_TYPE', ''):
            raise BadRequest('Not a Protobuf request')
        obj = proto_type()
        try:
            obj.ParseFromString(self.data)
        except Exception:
            raise BadRequest('Unable to parse Protobuf request')

        if self.protobuf_check_initialization and not obj.IsInitialized():
            raise BadRequest('Partial Protobuf request')
        return obj


class RoutingArgsRequestMixin(object):

    def _get_routing_args(self):
        return self.environ.get('wsgiorg.routing_args', ())[0]

    def _set_routing_args(self, value):
        if self.shallow:
            raise RuntimeError('A shallow request tried to modify the WSGI environment.  If you really want to do that, set `shallow` to False.')
        self.environ['wsgiorg.routing_args'] = (value, self.routing_vars)

    routing_args = property(_get_routing_args, _set_routing_args, doc='\n        The positional URL arguments as `tuple`.')
    del _get_routing_args
    del _set_routing_args

    def _get_routing_vars(self):
        rv = self.environ.get('wsgiorg.routing_args')
        if rv is not None:
            return rv[1]
        rv = {}
        if not self.shallow:
            self.routing_vars = rv
        return rv

    def _set_routing_vars(self, value):
        if self.shallow:
            raise RuntimeError('A shallow request tried to modify the WSGI environment.  If you really want to do that, set `shallow` to False.')
        self.environ['wsgiorg.routing_args'] = (self.routing_args, value)

    routing_vars = property(_get_routing_vars, _set_routing_vars, doc='\n        The keyword URL arguments as `dict`.')
    del _get_routing_vars
    del _set_routing_vars


class ReverseSlashBehaviorRequestMixin(object):

    @cached_property
    def path(self):
        path = (self.environ.get('PATH_INFO') or '').lstrip('/')
        return _decode_unicode(path, self.charset, self.encoding_errors)

    @cached_property
    def script_root(self):
        path = (self.environ.get('SCRIPT_NAME') or '').rstrip('/') + '/'
        return _decode_unicode(path, self.charset, self.encoding_errors)


class DynamicCharsetRequestMixin(object):
    default_charset = 'latin1'

    def unknown_charset(self, charset):
        return 'latin1'

    @cached_property
    def charset(self):
        header = self.environ.get('CONTENT_TYPE')
        if header:
            ct, options = parse_options_header(header)
            charset = options.get('charset')
            if charset:
                if is_known_charset(charset):
                    return charset
                return self.unknown_charset(charset)
        return self.default_charset


class DynamicCharsetResponseMixin(object):
    default_charset = 'utf-8'

    def _get_charset(self):
        header = self.headers.get('content-type')
        if header:
            charset = parse_options_header(header)[1].get('charset')
            if charset:
                return charset
        return self.default_charset

    def _set_charset(self, charset):
        header = self.headers.get('content-type')
        ct, options = parse_options_header(header)
        if not ct:
            raise TypeError('Cannot set charset if Content-Type header is missing.')
        options['charset'] = charset
        self.headers['Content-Type'] = dump_options_header(ct, options)

    charset = property(_get_charset, _set_charset, doc="\n        The charset for the response.  It's stored inside the\n        Content-Type header as a parameter.")
    del _get_charset
    del _set_charset