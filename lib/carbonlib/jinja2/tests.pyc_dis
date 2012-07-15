#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\tests.py
import re
from jinja2.runtime import Undefined
try:
    from collections import Mapping as MappingType
except ImportError:
    import UserDict
    MappingType = (UserDict.UserDict, UserDict.DictMixin, dict)

__test__ = False
number_re = re.compile('^-?\\d+(\\.\\d+)?$')
regex_type = type(number_re)
try:
    test_callable = callable
except NameError:

    def test_callable(x):
        return hasattr(x, '__call__')


def test_odd(value):
    return value % 2 == 1


def test_even(value):
    return value % 2 == 0


def test_divisibleby(value, num):
    return value % num == 0


def test_defined(value):
    return not isinstance(value, Undefined)


def test_undefined(value):
    return isinstance(value, Undefined)


def test_none(value):
    return value is None


def test_lower(value):
    return unicode(value).islower()


def test_upper(value):
    return unicode(value).isupper()


def test_string(value):
    return isinstance(value, basestring)


def test_mapping(value):
    return isinstance(value, MappingType)


def test_number(value):
    return isinstance(value, (int,
     long,
     float,
     complex))


def test_sequence(value):
    try:
        len(value)
        value.__getitem__
    except:
        return False

    return True


def test_sameas(value, other):
    return value is other


def test_iterable(value):
    try:
        iter(value)
    except TypeError:
        return False

    return True


def test_escaped(value):
    return hasattr(value, '__html__')


TESTS = {'odd': test_odd,
 'even': test_even,
 'divisibleby': test_divisibleby,
 'defined': test_defined,
 'undefined': test_undefined,
 'none': test_none,
 'lower': test_lower,
 'upper': test_upper,
 'string': test_string,
 'mapping': test_mapping,
 'number': test_number,
 'sequence': test_sequence,
 'iterable': test_iterable,
 'callable': test_callable,
 'sameas': test_sameas,
 'escaped': test_escaped}