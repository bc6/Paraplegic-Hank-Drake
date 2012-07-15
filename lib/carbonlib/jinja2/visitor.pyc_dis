#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\visitor.py
from jinja2.nodes import Node

class NodeVisitor(object):

    def get_visitor(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, None)

    def visit(self, node, *args, **kwargs):
        f = self.get_visitor(node)
        if f is not None:
            return f(node, *args, **kwargs)
        return self.generic_visit(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        for node in node.iter_child_nodes():
            self.visit(node, *args, **kwargs)


class NodeTransformer(NodeVisitor):

    def generic_visit(self, node, *args, **kwargs):
        for field, old_value in node.iter_fields():
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, Node):
                        value = self.visit(value, *args, **kwargs)
                        if value is None:
                            continue
                        elif not isinstance(value, Node):
                            new_values.extend(value)
                            continue
                    new_values.append(value)

                old_value[:] = new_values
            elif isinstance(old_value, Node):
                new_node = self.visit(old_value, *args, **kwargs)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)

        return node

    def visit_list(self, node, *args, **kwargs):
        rv = self.visit(node, *args, **kwargs)
        if not isinstance(rv, list):
            rv = [rv]
        return rv