from __future__ import with_statement
import contextlib
from error import *
from tokens import *
from events import *
from nodes import *
from loader import *
from dumper import *
__version__ = '3.09'
try:
    from cyaml import *
    __with_libyaml__ = True
except ImportError:
    __with_libyaml__ = False

@contextlib.contextmanager
def ClearState(f):
    try:
        yield f

    finally:
        f.state = f.states = None




def scan(stream, Loader = Loader):
    with ClearState(Loader(stream)) as loader:
        while loader.check_token():
            yield loader.get_token()




def parse(stream, Loader = Loader):
    loader = Loader(stream)
    with ClearState(loader):
        while loader.check_event():
            yield loader.get_event()




def compose(stream, Loader = Loader):
    loader = Loader(stream)
    with ClearState(loader):
        return loader.get_single_node()



def compose_all(stream, Loader = Loader):
    loader = Loader(stream)
    with ClearState(loader):
        while loader.check_node():
            yield loader.get_node()




def load(stream, Loader = Loader):
    loader = Loader(stream)
    with ClearState(loader):
        return loader.get_single_data()



def load_all(stream, Loader = Loader):
    loader = Loader(stream)
    with ClearState(loader):
        while loader.check_data():
            yield loader.get_data()




def safe_load(stream):
    return load(stream, SafeLoader)



def safe_load_all(stream):
    return load_all(stream, SafeLoader)



def emit(events, stream = None, Dumper = Dumper, canonical = None, indent = None, width = None, allow_unicode = None, line_break = None):
    getvalue = None
    if stream is None:
        from StringIO import StringIO
        stream = StringIO()
        getvalue = stream.getvalue
    dumper = Dumper(stream, canonical=canonical, indent=indent, width=width, allow_unicode=allow_unicode, line_break=line_break)
    with ClearState(dumper):
        for event in events:
            dumper.emit(event)

        if getvalue:
            return getvalue()



def serialize_all(nodes, stream = None, Dumper = Dumper, canonical = None, indent = None, width = None, allow_unicode = None, line_break = None, encoding = 'utf-8', explicit_start = None, explicit_end = None, version = None, tags = None):
    getvalue = None
    if stream is None:
        if encoding is None:
            from StringIO import StringIO
        else:
            from cStringIO import StringIO
        stream = StringIO()
        getvalue = stream.getvalue
    dumper = Dumper(stream, canonical=canonical, indent=indent, width=width, allow_unicode=allow_unicode, line_break=line_break, encoding=encoding, version=version, tags=tags, explicit_start=explicit_start, explicit_end=explicit_end)
    dumper.open()
    with ClearState(dumper):
        for node in nodes:
            dumper.serialize(node)

        dumper.close()
        if getvalue:
            return getvalue()



def serialize(node, stream = None, Dumper = Dumper, **kwds):
    return serialize_all([node], stream, Dumper=Dumper, **kwds)



def dump_all(documents, stream = None, Dumper = Dumper, default_style = None, default_flow_style = None, canonical = None, indent = None, width = None, allow_unicode = None, line_break = None, encoding = 'utf-8', explicit_start = None, explicit_end = None, version = None, tags = None):
    getvalue = None
    if stream is None:
        if encoding is None:
            from StringIO import StringIO
        else:
            from cStringIO import StringIO
        stream = StringIO()
        getvalue = stream.getvalue
    dumper = Dumper(stream, default_style=default_style, default_flow_style=default_flow_style, canonical=canonical, indent=indent, width=width, allow_unicode=allow_unicode, line_break=line_break, encoding=encoding, version=version, tags=tags, explicit_start=explicit_start, explicit_end=explicit_end)
    dumper.open()
    with ClearState(dumper):
        for data in documents:
            dumper.represent(data)

        dumper.close()
        if getvalue:
            return getvalue()



def dump(data, stream = None, Dumper = Dumper, **kwds):
    return dump_all([data], stream, Dumper=Dumper, **kwds)



def safe_dump_all(documents, stream = None, **kwds):
    return dump_all(documents, stream, Dumper=SafeDumper, **kwds)



def safe_dump(data, stream = None, **kwds):
    return dump_all([data], stream, Dumper=SafeDumper, **kwds)



def add_implicit_resolver(tag, regexp, first = None, Loader = Loader, Dumper = Dumper):
    Loader.add_implicit_resolver(tag, regexp, first)
    Dumper.add_implicit_resolver(tag, regexp, first)



def add_path_resolver(tag, path, kind = None, Loader = Loader, Dumper = Dumper):
    Loader.add_path_resolver(tag, path, kind)
    Dumper.add_path_resolver(tag, path, kind)



def add_constructor(tag, constructor, Loader = Loader):
    Loader.add_constructor(tag, constructor)



def add_multi_constructor(tag_prefix, multi_constructor, Loader = Loader):
    Loader.add_multi_constructor(tag_prefix, multi_constructor)



def add_representer(data_type, representer, Dumper = Dumper):
    Dumper.add_representer(data_type, representer)



def add_multi_representer(data_type, multi_representer, Dumper = Dumper):
    Dumper.add_multi_representer(data_type, multi_representer)



class YAMLObjectMetaclass(type):

    def __init__(cls, name, bases, kwds):
        super(YAMLObjectMetaclass, cls).__init__(name, bases, kwds)
        if 'yaml_tag' in kwds and kwds['yaml_tag'] is not None:
            cls.yaml_loader.add_constructor(cls.yaml_tag, cls.from_yaml)
            cls.yaml_dumper.add_representer(cls, cls.to_yaml)




class YAMLObject(object):
    __metaclass__ = YAMLObjectMetaclass
    __slots__ = ()
    yaml_loader = Loader
    yaml_dumper = Dumper
    yaml_tag = None
    yaml_flow_style = None

    def from_yaml(cls, loader, node):
        return loader.construct_yaml_object(node, cls)


    from_yaml = classmethod(from_yaml)

    def to_yaml(cls, dumper, data):
        return dumper.represent_yaml_object(cls.yaml_tag, data, cls, flow_style=cls.yaml_flow_style)


    to_yaml = classmethod(to_yaml)


