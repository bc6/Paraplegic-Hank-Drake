__author_name__ = 'Ben Finney'
__author_email__ = 'ben+python@benfinney.id.au'
__author__ = '%(__author_name__)s <%(__author_email__)s>' % vars()
_copyright_year_begin = '2007'
__date__ = '2009-08-26'
_copyright_year_latest = __date__.split('-')[0]
_copyright_year_range = _copyright_year_begin
if _copyright_year_latest > _copyright_year_begin:
    _copyright_year_range += '\xe2\x80\x93%(_copyright_year_latest)s' % vars()
__copyright__ = 'Copyright \xc2\xa9 %(_copyright_year_range)s %(__author_name__)s' % vars()
__license__ = 'Choice of GPL or Python license'
__url__ = 'http://pypi.python.org/pypi/enum/'
__version__ = '0.4.4'

class EnumException(Exception):

    def __init__(self, *args, **kwargs):
        if self.__class__ is EnumException:
            class_name = self.__class__.__name__
            raise NotImplementedError('%(class_name)s is an abstract base class' % vars())
        super(EnumException, self).__init__(*args, **kwargs)




class EnumEmptyError(AssertionError, EnumException):

    def __str__(self):
        return 'Enumerations cannot be empty'




class EnumBadKeyError(TypeError, EnumException):

    def __init__(self, key):
        self.key = key



    def __str__(self):
        return 'Enumeration keys must be strings: %(key)r' % vars(self)




class EnumImmutableError(TypeError, EnumException):

    def __init__(self, *args):
        self.args = args



    def __str__(self):
        return 'Enumeration does not allow modification'




def _comparator(func):

    def comparator_wrapper(self, other):
        try:
            result = func(self.index, other.index)
        except (AssertionError, AttributeError):
            result = NotImplemented
        return result


    comparator_wrapper.__name__ = func.__name__
    comparator_wrapper.__doc__ = getattr(float, func.__name__).__doc__
    return comparator_wrapper



class EnumValue(object):

    def __init__(self, enumtype, index, key):
        self._enumtype = enumtype
        self._index = index
        self._key = key



    @property
    def enumtype(self):
        return self._enumtype



    @property
    def key(self):
        return self._key



    def __str__(self):
        return str(self.key)



    @property
    def index(self):
        return self._index



    def __repr__(self):
        return 'EnumValue(%(_enumtype)r, %(_index)r, %(_key)r)' % vars(self)



    def __hash__(self):
        return hash(self._index)



    @_comparator
    def __eq__(self, other):
        return self == other



    @_comparator
    def __ne__(self, other):
        return self != other



    @_comparator
    def __lt__(self, other):
        return self < other



    @_comparator
    def __le__(self, other):
        return self <= other



    @_comparator
    def __gt__(self, other):
        return self > other



    @_comparator
    def __ge__(self, other):
        return self >= other




class Enum(object):

    def __init__(self, *keys, **kwargs):
        value_type = kwargs.get('value_type', EnumValue)
        if not keys:
            raise EnumEmptyError()
        keys = tuple(keys)
        values = [None] * len(keys)
        for (i, key,) in enumerate(keys):
            value = value_type(self, i, key)
            values[i] = value
            try:
                super(Enum, self).__setattr__(key, value)
            except TypeError:
                raise EnumBadKeyError(key)

        self.__dict__['_keys'] = keys
        self.__dict__['_values'] = values



    def __setattr__(self, name, value):
        raise EnumImmutableError(name)



    def __delattr__(self, name):
        raise EnumImmutableError(name)



    def __len__(self):
        return len(self._values)



    def __getitem__(self, index):
        return self._values[index]



    def __setitem__(self, index, value):
        raise EnumImmutableError(index)



    def __delitem__(self, index):
        raise EnumImmutableError(index)



    def __iter__(self):
        return iter(self._values)



    def __contains__(self, value):
        is_member = False
        if isinstance(value, basestring):
            is_member = value in self._keys
        else:
            is_member = value in self._values
        return is_member




