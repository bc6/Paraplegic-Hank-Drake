#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\sandbox.py
import operator
from jinja2.environment import Environment
from jinja2.exceptions import SecurityError
from jinja2.utils import FunctionType, MethodType, TracebackType, CodeType, FrameType, GeneratorType
MAX_RANGE = 100000
UNSAFE_FUNCTION_ATTRIBUTES = set(['func_closure',
 'func_code',
 'func_dict',
 'func_defaults',
 'func_globals'])
UNSAFE_METHOD_ATTRIBUTES = set(['im_class', 'im_func', 'im_self'])
import warnings
warnings.filterwarnings('ignore', 'the sets module', DeprecationWarning, module='jinja2.sandbox')
from collections import deque
_mutable_set_types = (set,)
_mutable_mapping_types = (dict,)
_mutable_sequence_types = (list,)
try:
    from UserDict import UserDict, DictMixin
    from UserList import UserList
    _mutable_mapping_types += (UserDict, DictMixin)
    _mutable_set_types += (UserList,)
except ImportError:
    pass

try:
    from sets import Set
    _mutable_set_types += (Set,)
except ImportError:
    pass

try:
    from collections import MutableSet, MutableMapping, MutableSequence
    _mutable_set_types += (MutableSet,)
    _mutable_mapping_types += (MutableMapping,)
    _mutable_sequence_types += (MutableSequence,)
except ImportError:
    pass

_mutable_spec = ((_mutable_set_types, frozenset(['add',
   'clear',
   'difference_update',
   'discard',
   'pop',
   'remove',
   'symmetric_difference_update',
   'update'])),
 (_mutable_mapping_types, frozenset(['clear',
   'pop',
   'popitem',
   'setdefault',
   'update'])),
 (_mutable_sequence_types, frozenset(['append',
   'reverse',
   'insert',
   'sort',
   'extend',
   'remove'])),
 (deque, frozenset(['append',
   'appendleft',
   'clear',
   'extend',
   'extendleft',
   'pop',
   'popleft',
   'remove',
   'rotate'])))

def safe_range(*args):
    rng = xrange(*args)
    if len(rng) > MAX_RANGE:
        raise OverflowError('range too big, maximum size for range is %d' % MAX_RANGE)
    return rng


def unsafe(f):
    f.unsafe_callable = True
    return f


def is_internal_attribute(obj, attr):
    if isinstance(obj, FunctionType):
        if attr in UNSAFE_FUNCTION_ATTRIBUTES:
            return True
    elif isinstance(obj, MethodType):
        if attr in UNSAFE_FUNCTION_ATTRIBUTES or attr in UNSAFE_METHOD_ATTRIBUTES:
            return True
    elif isinstance(obj, type):
        if attr == 'mro':
            return True
    else:
        if isinstance(obj, (CodeType, TracebackType, FrameType)):
            return True
        if isinstance(obj, GeneratorType):
            if attr == 'gi_frame':
                return True
    return attr.startswith('__')


def modifies_known_mutable(obj, attr):
    for typespec, unsafe in _mutable_spec:
        if isinstance(obj, typespec):
            return attr in unsafe

    return False


class SandboxedEnvironment(Environment):
    sandboxed = True
    default_binop_table = {'+': operator.add,
     '-': operator.sub,
     '*': operator.mul,
     '/': operator.truediv,
     '//': operator.floordiv,
     '**': operator.pow,
     '%': operator.mod}
    default_unop_table = {'+': operator.pos,
     '-': operator.neg}
    intercepted_binops = frozenset()
    intercepted_unops = frozenset()

    def intercept_unop(self, operator):
        return False

    def __init__(self, *args, **kwargs):
        Environment.__init__(self, *args, **kwargs)
        self.globals['range'] = safe_range
        self.binop_table = self.default_binop_table.copy()
        self.unop_table = self.default_unop_table.copy()

    def is_safe_attribute(self, obj, attr, value):
        return not (attr.startswith('_') or is_internal_attribute(obj, attr))

    def is_safe_callable(self, obj):
        return not (getattr(obj, 'unsafe_callable', False) or getattr(obj, 'alters_data', False))

    def call_binop(self, context, operator, left, right):
        return self.binop_table[operator](left, right)

    def call_unop(self, context, operator, arg):
        return self.unop_table[operator](arg)

    def getitem(self, obj, argument):
        try:
            return obj[argument]
        except (TypeError, LookupError):
            if isinstance(argument, basestring):
                try:
                    attr = str(argument)
                except Exception:
                    pass
                else:
                    try:
                        value = getattr(obj, attr)
                    except AttributeError:
                        pass
                    else:
                        if self.is_safe_attribute(obj, argument, value):
                            return value
                        return self.unsafe_undefined(obj, argument)

        return self.undefined(obj=obj, name=argument)

    def getattr(self, obj, attribute):
        try:
            value = getattr(obj, attribute)
        except AttributeError:
            try:
                return obj[attribute]
            except (TypeError, LookupError):
                pass

        else:
            if self.is_safe_attribute(obj, attribute, value):
                return value
            return self.unsafe_undefined(obj, attribute)

        return self.undefined(obj=obj, name=attribute)

    def unsafe_undefined(self, obj, attribute):
        return self.undefined('access to attribute %r of %r object is unsafe.' % (attribute, obj.__class__.__name__), name=attribute, obj=obj, exc=SecurityError)

    def call(_SandboxedEnvironment__self, _SandboxedEnvironment__context, _SandboxedEnvironment__obj, *args, **kwargs):
        if not __self.is_safe_callable(__obj):
            raise SecurityError('%r is not safely callable' % (__obj,))
        return __context.call(__obj, *args, **kwargs)


class ImmutableSandboxedEnvironment(SandboxedEnvironment):

    def is_safe_attribute(self, obj, attr, value):
        if not SandboxedEnvironment.is_safe_attribute(self, obj, attr, value):
            return False
        return not modifies_known_mutable(obj, attr)