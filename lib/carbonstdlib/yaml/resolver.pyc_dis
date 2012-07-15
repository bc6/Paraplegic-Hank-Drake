#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\yaml\resolver.py
__all__ = ['BaseResolver', 'Resolver']
from error import *
from nodes import *
import re

class ResolverError(YAMLError):
    pass


class BaseResolver(object):
    DEFAULT_SCALAR_TAG = u'tag:yaml.org,2002:str'
    DEFAULT_SEQUENCE_TAG = u'tag:yaml.org,2002:seq'
    DEFAULT_MAPPING_TAG = u'tag:yaml.org,2002:map'
    yaml_implicit_resolvers = {}
    yaml_path_resolvers = {}

    def __init__(self):
        self.resolver_exact_paths = []
        self.resolver_prefix_paths = []

    def add_implicit_resolver(cls, tag, regexp, first):
        if 'yaml_implicit_resolvers' not in cls.__dict__:
            cls.yaml_implicit_resolvers = cls.yaml_implicit_resolvers.copy()
        if first is None:
            first = [None]
        for ch in first:
            cls.yaml_implicit_resolvers.setdefault(ch, []).append((tag, regexp))

    add_implicit_resolver = classmethod(add_implicit_resolver)

    def add_path_resolver(cls, tag, path, kind = None):
        if 'yaml_path_resolvers' not in cls.__dict__:
            cls.yaml_path_resolvers = cls.yaml_path_resolvers.copy()
        new_path = []
        for element in path:
            if isinstance(element, (list, tuple)):
                if len(element) == 2:
                    node_check, index_check = element
                elif len(element) == 1:
                    node_check = element[0]
                    index_check = True
                else:
                    raise ResolverError('Invalid path element: %s' % element)
            else:
                node_check = None
                index_check = element
            if node_check is str:
                node_check = ScalarNode
            elif node_check is list:
                node_check = SequenceNode
            elif node_check is dict:
                node_check = MappingNode
            elif node_check not in [ScalarNode, SequenceNode, MappingNode] and not isinstance(node_check, basestring) and node_check is not None:
                raise ResolverError('Invalid node checker: %s' % node_check)
            if not isinstance(index_check, (basestring, int)) and index_check is not None:
                raise ResolverError('Invalid index checker: %s' % index_check)
            new_path.append((node_check, index_check))

        if kind is str:
            kind = ScalarNode
        elif kind is list:
            kind = SequenceNode
        elif kind is dict:
            kind = MappingNode
        elif kind not in [ScalarNode, SequenceNode, MappingNode] and kind is not None:
            raise ResolverError('Invalid node kind: %s' % kind)
        cls.yaml_path_resolvers[tuple(new_path), kind] = tag

    add_path_resolver = classmethod(add_path_resolver)

    def descend_resolver(self, current_node, current_index):
        if not self.yaml_path_resolvers:
            return
        exact_paths = {}
        prefix_paths = []
        if current_node:
            depth = len(self.resolver_prefix_paths)
            for path, kind in self.resolver_prefix_paths[-1]:
                if self.check_resolver_prefix(depth, path, kind, current_node, current_index):
                    if len(path) > depth:
                        prefix_paths.append((path, kind))
                    else:
                        exact_paths[kind] = self.yaml_path_resolvers[path, kind]

        else:
            for path, kind in self.yaml_path_resolvers:
                if not path:
                    exact_paths[kind] = self.yaml_path_resolvers[path, kind]
                else:
                    prefix_paths.append((path, kind))

        self.resolver_exact_paths.append(exact_paths)
        self.resolver_prefix_paths.append(prefix_paths)

    def ascend_resolver(self):
        if not self.yaml_path_resolvers:
            return
        self.resolver_exact_paths.pop()
        self.resolver_prefix_paths.pop()

    def check_resolver_prefix(self, depth, path, kind, current_node, current_index):
        node_check, index_check = path[depth - 1]
        if isinstance(node_check, basestring):
            if current_node.tag != node_check:
                return
        elif node_check is not None:
            if not isinstance(current_node, node_check):
                return
        if index_check is True and current_index is not None:
            return
        if (index_check is False or index_check is None) and current_index is None:
            return
        if isinstance(index_check, basestring):
            if not (isinstance(current_index, ScalarNode) and index_check == current_index.value):
                return
        elif isinstance(index_check, int) and not isinstance(index_check, bool):
            if index_check != current_index:
                return
        return True

    def resolve(self, kind, value, implicit):
        if kind is ScalarNode and implicit[0]:
            if value == u'':
                resolvers = self.yaml_implicit_resolvers.get(u'', [])
            else:
                resolvers = self.yaml_implicit_resolvers.get(value[0], [])
            resolvers += self.yaml_implicit_resolvers.get(None, [])
            for tag, regexp in resolvers:
                if regexp.match(value):
                    return tag

            implicit = implicit[1]
        if self.yaml_path_resolvers:
            exact_paths = self.resolver_exact_paths[-1]
            if kind in exact_paths:
                return exact_paths[kind]
            if None in exact_paths:
                return exact_paths[None]
        if kind is ScalarNode:
            return self.DEFAULT_SCALAR_TAG
        if kind is SequenceNode:
            return self.DEFAULT_SEQUENCE_TAG
        if kind is MappingNode:
            return self.DEFAULT_MAPPING_TAG


class Resolver(BaseResolver):
    pass


Resolver.add_implicit_resolver(u'tag:yaml.org,2002:bool', re.compile(u'^(?:yes|Yes|YES|no|No|NO\n                    |true|True|TRUE|false|False|FALSE\n                    |on|On|ON|off|Off|OFF)$', re.X), list(u'yYnNtTfFoO'))
Resolver.add_implicit_resolver(u'tag:yaml.org,2002:float', re.compile(u'^(?:[-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+][0-9]+)?\n                    |\\.[0-9_]+(?:[eE][-+][0-9]+)?\n                    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*\n                    |[-+]?\\.(?:inf|Inf|INF)\n                    |\\.(?:nan|NaN|NAN))$', re.X), list(u'-+0123456789.'))
Resolver.add_implicit_resolver(u'tag:yaml.org,2002:int', re.compile(u'^(?:[-+]?0b[0-1_]+\n                    |[-+]?0[0-7_]+\n                    |[-+]?(?:0|[1-9][0-9_]*)\n                    |[-+]?0x[0-9a-fA-F_]+\n                    |[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+)$', re.X), list(u'-+0123456789'))
Resolver.add_implicit_resolver(u'tag:yaml.org,2002:merge', re.compile(u'^(?:<<)$'), [u'<'])
Resolver.add_implicit_resolver(u'tag:yaml.org,2002:null', re.compile(u'^(?: ~\n                    |null|Null|NULL\n                    | )$', re.X), [u'~',
 u'n',
 u'N',
 u''])
Resolver.add_implicit_resolver(u'tag:yaml.org,2002:timestamp', re.compile(u'^(?:[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\n                    |[0-9][0-9][0-9][0-9] -[0-9][0-9]? -[0-9][0-9]?\n                     (?:[Tt]|[ \\t]+)[0-9][0-9]?\n                     :[0-9][0-9] :[0-9][0-9] (?:\\.[0-9]*)?\n                     (?:[ \\t]*(?:Z|[-+][0-9][0-9]?(?::[0-9][0-9])?))?)$', re.X), list(u'0123456789'))
Resolver.add_implicit_resolver(u'tag:yaml.org,2002:value', re.compile(u'^(?:=)$'), [u'='])
Resolver.add_implicit_resolver(u'tag:yaml.org,2002:yaml', re.compile(u'^(?:!|&|\\*)$'), list(u'!&*'))