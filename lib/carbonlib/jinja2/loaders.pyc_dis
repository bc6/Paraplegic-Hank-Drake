#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\loaders.py
import os
import sys
import weakref
from types import ModuleType
from os import path
try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1

from jinja2.exceptions import TemplateNotFound
from jinja2.utils import LRUCache, open_if_exists, internalcode

def split_template_path(template):
    pieces = []
    for piece in template.split('/'):
        if path.sep in piece or path.altsep and path.altsep in piece or piece == path.pardir:
            raise TemplateNotFound(template)
        elif piece and piece != '.':
            pieces.append(piece)

    return pieces


class BaseLoader(object):
    has_source_access = True

    def get_source(self, environment, template):
        if not self.has_source_access:
            raise RuntimeError('%s cannot provide access to the source' % self.__class__.__name__)
        raise TemplateNotFound(template)

    def list_templates(self):
        raise TypeError('this loader cannot iterate over all templates')

    @internalcode
    def load(self, environment, name, globals = None):
        code = None
        if globals is None:
            globals = {}
        source, filename, uptodate = self.get_source(environment, name)
        bcc = environment.bytecode_cache
        if bcc is not None:
            bucket = bcc.get_bucket(environment, name, filename, source)
            code = bucket.code
        if code is None:
            code = environment.compile(source, name, filename)
        if bcc is not None and bucket.code is None:
            bucket.code = code
            bcc.set_bucket(bucket)
        return environment.template_class.from_code(environment, code, globals, uptodate)


class FileSystemLoader(BaseLoader):

    def __init__(self, searchpath, encoding = 'utf-8'):
        if isinstance(searchpath, basestring):
            searchpath = [searchpath]
        self.searchpath = list(searchpath)
        self.encoding = encoding

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = path.join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = path.getmtime(filename)

            def uptodate():
                try:
                    return path.getmtime(filename) == mtime
                except OSError:
                    return False

            return (contents, filename, uptodate)

        raise TemplateNotFound(template)

    def list_templates(self):
        found = set()
        for searchpath in self.searchpath:
            for dirpath, dirnames, filenames in os.walk(searchpath):
                for filename in filenames:
                    template = os.path.join(dirpath, filename)[len(searchpath):].strip(os.path.sep).replace(os.path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)

        return sorted(found)


class PackageLoader(BaseLoader):

    def __init__(self, package_name, package_path = 'templates', encoding = 'utf-8'):
        from pkg_resources import DefaultProvider, ResourceManager, get_provider
        provider = get_provider(package_name)
        self.encoding = encoding
        self.manager = ResourceManager()
        self.filesystem_bound = isinstance(provider, DefaultProvider)
        self.provider = provider
        self.package_path = package_path

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        p = '/'.join((self.package_path,) + tuple(pieces))
        if not self.provider.has_resource(p):
            raise TemplateNotFound(template)
        filename = uptodate = None
        if self.filesystem_bound:
            filename = self.provider.get_resource_filename(self.manager, p)
            mtime = path.getmtime(filename)

            def uptodate():
                try:
                    return path.getmtime(filename) == mtime
                except OSError:
                    return False

        source = self.provider.get_resource_string(self.manager, p)
        return (source.decode(self.encoding), filename, uptodate)

    def list_templates(self):
        path = self.package_path
        if path[:2] == './':
            path = path[2:]
        elif path == '.':
            path = ''
        offset = len(path)
        results = []

        def _walk(path):
            for filename in self.provider.resource_listdir(path):
                fullname = path + '/' + filename
                if self.provider.resource_isdir(fullname):
                    _walk(fullname)
                else:
                    results.append(fullname[offset:].lstrip('/'))

        _walk(path)
        results.sort()
        return results


class DictLoader(BaseLoader):

    def __init__(self, mapping):
        self.mapping = mapping

    def get_source(self, environment, template):
        if template in self.mapping:
            source = self.mapping[template]
            return (source, None, lambda : source != self.mapping.get(template))
        raise TemplateNotFound(template)

    def list_templates(self):
        return sorted(self.mapping)


class FunctionLoader(BaseLoader):

    def __init__(self, load_func):
        self.load_func = load_func

    def get_source(self, environment, template):
        rv = self.load_func(template)
        if rv is None:
            raise TemplateNotFound(template)
        elif isinstance(rv, basestring):
            return (rv, None, None)
        return rv


class PrefixLoader(BaseLoader):

    def __init__(self, mapping, delimiter = '/'):
        self.mapping = mapping
        self.delimiter = delimiter

    def get_loader(self, template):
        try:
            prefix, name = template.split(self.delimiter, 1)
            loader = self.mapping[prefix]
        except (ValueError, KeyError):
            raise TemplateNotFound(template)

        return (loader, name)

    def get_source(self, environment, template):
        loader, name = self.get_loader(template)
        try:
            return loader.get_source(environment, name)
        except TemplateNotFound:
            raise TemplateNotFound(template)

    @internalcode
    def load(self, environment, name, globals = None):
        loader, local_name = self.get_loader(name)
        try:
            return loader.load(environment, local_name)
        except TemplateNotFound:
            raise TemplateNotFound(name)

    def list_templates(self):
        result = []
        for prefix, loader in self.mapping.iteritems():
            for template in loader.list_templates():
                result.append(prefix + self.delimiter + template)

        return result


class ChoiceLoader(BaseLoader):

    def __init__(self, loaders):
        self.loaders = loaders

    def get_source(self, environment, template):
        for loader in self.loaders:
            try:
                return loader.get_source(environment, template)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template)

    @internalcode
    def load(self, environment, name, globals = None):
        for loader in self.loaders:
            try:
                return loader.load(environment, name, globals)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(name)

    def list_templates(self):
        found = set()
        for loader in self.loaders:
            found.update(loader.list_templates())

        return sorted(found)


class _TemplateModule(ModuleType):
    pass


class ModuleLoader(BaseLoader):
    has_source_access = False

    def __init__(self, path):
        package_name = '_jinja2_module_templates_%x' % id(self)
        mod = _TemplateModule(package_name)
        if isinstance(path, basestring):
            path = [path]
        else:
            path = list(path)
        mod.__path__ = path
        sys.modules[package_name] = weakref.proxy(mod, lambda x: sys.modules.pop(package_name, None))
        self.module = mod
        self.package_name = package_name

    @staticmethod
    def get_template_key(name):
        return 'tmpl_' + sha1(name.encode('utf-8')).hexdigest()

    @staticmethod
    def get_module_filename(name):
        return ModuleLoader.get_template_key(name) + '.py'

    @internalcode
    def load(self, environment, name, globals = None):
        key = self.get_template_key(name)
        module = '%s.%s' % (self.package_name, key)
        mod = getattr(self.module, module, None)
        if mod is None:
            try:
                mod = __import__(module, None, None, ['root'])
            except ImportError:
                raise TemplateNotFound(name)

            sys.modules.pop(module, None)
        return environment.template_class.from_module_dict(environment, mod.__dict__, globals)